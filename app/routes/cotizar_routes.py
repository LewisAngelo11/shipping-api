# Endpoints de los metodos para cotizar envios

from flask import Blueprint, request, jsonify
from sqlalchemy import select

from geopy.distance import geodesic   #libreria para posteriormente obtener distancias entre destino y origen de un paquete
from app.config.config_sqlalchemy import get_session

# Se importan los modelos a utilizar en los endpoints
from app.models.codigos_postales import CodigosPostales
from app.models.municipio import Municipio
from app.models.entidad_federativa import EntidadFederativa
from app.models.localidad import Localidad

cotizar_bp = Blueprint('cotizar', __name__)


# Función para calcular la distancia y convertirla a la tarifa de envio
def calcularDistancia(distancia):
    if (distancia) >= 0 and distancia <= 199:
        return 100
    elif (distancia) >= 200 and distancia <= 499:
        return 150
    elif distancia >= 500 and distancia <= 799:
        return 220


# Función para la estructura de la query de cotizar un envio (Como se utilizará dos veces, se hizo funcion para no tener codigo repetido)
def execute_query(localidad, municipio, entidad):
    stmt = (
        select(
            Localidad.Id_EntidadFed,
            Localidad.Id_Municipio,
            Localidad.Id_Localidad,
            Localidad.NOM_LOC,
            Localidad.LAT_DECIMAL,
            Localidad.LON_DECIMAL
        )
        .select_from(Localidad)
        .join(
            Municipio,
            (Municipio.Id_EntidadFed == Localidad.Id_EntidadFed) &
            (Municipio.Id_Municipio == Localidad.Id_Municipio)
        ).join(
            EntidadFederativa,
            EntidadFederativa.Id_EntidadFed == Municipio.Id_EntidadFed
        )
        .filter(
            Localidad.NOM_LOC == localidad,
            Municipio.Nombre == municipio,
            EntidadFederativa.Nombre == entidad
        )
    )
    return stmt


# Función para retornar los valores de Municipio y Estado con el codigo postal.
@cotizar_bp.route("/Cotizar/CP", methods=["POST"])
def ConsultarPorCP():
    datos = request.json
    CP = datos.get("CP")
    print("Datos recibidos en Flask:", datos)
    print(CP)
    db = get_session()
    try:
        # Este es el query para obtener la cd,municipio,estado del cp que ingresamos
        stmt = (
            select(
                Municipio.Nombre.label('municipio'),
                EntidadFederativa.Nombre.label('entidad'),
                Localidad.NOM_LOC.label('localidad')
            )
            .select_from(CodigosPostales)
            .join(
                Municipio,
                (CodigosPostales.C_Estado == Municipio.Id_EntidadFed) &
                (CodigosPostales.C_Mun == Municipio.Id_Municipio)
            ).join(
                EntidadFederativa,
                Municipio.Id_EntidadFed == EntidadFederativa.Id_EntidadFed
            ).join(
                Localidad,
                (Municipio.Id_EntidadFed == Localidad.Id_EntidadFed) &
                (Municipio.Id_Municipio == Localidad.Id_Municipio)
            ).filter(
                CodigosPostales.CP == CP
            )
        )

        result = db.execute(stmt).first() # Ejecuta la query

        if result:
            print(result.municipio, result.entidad, result.localidad) # Imprime los valores devueltos en la query
            # Una vez acabado es obligatorio mandar una respuesta y en esta respuesta ponemos success como exitoso y los datos cd,mun,estado
            return jsonify({
                "status": "success",
                "municipio": result.municipio,
                "entidad": result.entidad,
                "localidad": result.localidad
            }), 200
        else:
            return jsonify({"status": "error", "mensaje": "No se encontraron datos"}), 404
    except Exception as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        db.close()


# Función para cotizar un paquete
@cotizar_bp.route("/Cotizar/Paquete", methods=["POST"])
def CotizarPaquete():
    datos = request.json  # Obtiene los datos del archivo json de la pagina web

    # Datos del origen
    localidad_origen = datos.get('LocalidadO')
    municipio_origen = datos.get('MunicipioO')
    entidad_origen = datos.get('EntidadO')
    # Datos del destino
    localidad_destino = datos.get('LocalidadD')
    municipio_destino = datos.get('MunicipioD')
    entidad_destino = datos.get('EntidadD')

    print("Datos recibidos en Flask:", datos)
    PesoVM = (int(datos['Largo']) * int(datos['Ancho']) * int(datos['Alto']))/6000
    print(str(PesoVM))
    db = get_session()
    try:
        # Llama a la función para ejecutar la query
        stmt_origen = execute_query(localidad_origen, municipio_origen, entidad_origen)

        result_origen = db.execute(stmt_origen).first()  # Ejecuta la query
        if result_origen:
            latitud_origen = result_origen[4]
            longitud_origen = result_origen[5]
            print(latitud_origen)
            print(longitud_origen)
            try:
                # Llama a la función para ejecutar la query
                stmt_destino = execute_query(localidad_destino, municipio_destino, entidad_destino)

                result_destino = db.execute(stmt_destino).first()  # Ejecuta la query nuevamente
                tarifa = 0
                if result_destino:
                    latitud_destino = result_destino[4]
                    longitud_destino = result_destino[5]
                    coords_1 = (float(latitud_origen), float(longitud_origen))
                    coords_2 = (float(latitud_destino),float(longitud_destino))
                    distancia = round(geodesic(coords_1, coords_2).kilometers, 2) # Devolver la distancia en kilometros
                    print(distancia)
                    tarifa = calcularDistancia(distancia) # Llama a la función para calcular la distancia y la convierte en la tarifa del envio
                    print(tarifa)
                    pesomax = max(PesoVM,int(datos['Peso']))
                    tarifa_base = 10
                    tarifa = tarifa + (tarifa_base * int(pesomax))
                    print(tarifa)
            except Exception as err:
                return jsonify({"status": "error", "mensaje": str(err)}), 400
            return jsonify({"status": "success","tarifa": str(tarifa), "pesovm": str(PesoVM), "distancia": str(distancia)}), 200
    except Exception as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        db.close()
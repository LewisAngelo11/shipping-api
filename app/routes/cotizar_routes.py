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
from datetime import datetime, timedelta

cotizar_bp = Blueprint('cotizar', __name__)


# Función para calcular la distancia, convertirla a tarifa de envío y calcular fecha estimada
def calcularDistancia(distancia):
    # Calcular tarifa según distancia
    if distancia >= 0 and distancia <= 199:
        tarifa = 50
        dias_entrega = 1
    elif distancia >= 200 and distancia <= 499:
        tarifa = 100
        dias_entrega = 3
    elif distancia >= 500 and distancia <= 799:
        tarifa = 150
        dias_entrega = 5
    else:
        tarifa = 200
        dias_entrega = 7

    # Calcular fecha estimada de entrega
    fecha_actual = datetime.now()
    fecha_entrega = fecha_actual + timedelta(days=dias_entrega)

    return {
        'tarifa': tarifa,
        'dias_entrega': dias_entrega,
        'fecha_entrega': fecha_entrega.strftime('%d/%m/%Y')
    }

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
        # Query para obtener TODOS los asentamientos del CP
        stmt = (
            select(
                Municipio.Nombre.label('municipio'),
                EntidadFederativa.Nombre.label('entidad'),
                Localidad.NOM_LOC.label('localidad'),
                CodigosPostales.Asentamiento.label('asentamiento')
            )
            .select_from(CodigosPostales)
            .join(
                Municipio,
                (CodigosPostales.C_Estado == Municipio.Id_EntidadFed) &
                (CodigosPostales.C_Mun == Municipio.Id_Municipio)
            )
            .join(
                EntidadFederativa,
                Municipio.Id_EntidadFed == EntidadFederativa.Id_EntidadFed
            )
            .join(
                Localidad,
                (Municipio.Id_EntidadFed == Localidad.Id_EntidadFed) &
                (Municipio.Id_Municipio == Localidad.Id_Municipio)
            )
            .filter(CodigosPostales.CP == CP)
            .distinct()  # Evita duplicados
        )

        results = db.execute(stmt).all()

        if results:
            # Extraer datos únicos
            municipio = results[0].municipio
            entidad = results[0].entidad
            localidad = results[0].localidad

            # Obtener todos los asentamientos únicos
            asentamientos = list(set([r.asentamiento for r in results if r.asentamiento]))

            print(f"CP {CP}: {len(asentamientos)} asentamientos encontrados")

            return jsonify({
                "status": "success",
                "municipio": municipio,
                "entidad": entidad,
                "localidad": localidad,
                "asentamientos": asentamientos  # Lista de todos los asentamientos
            }), 200
        else:
            return jsonify({
                "status": "error",
                "mensaje": "No se encontraron datos para el código postal proporcionado"
            }), 404

    except Exception as err:
        print(f"Error en ConsultarPorCP: {str(err)}")
        return jsonify({
            "status": "error",
            "mensaje": f"Error al procesar la solicitud: {str(err)}"
        }), 400
    finally:
        db.close()


# Función para cotizar un paquete
@cotizar_bp.route("/Cotizar/Paquete", methods=["POST"])
def CotizarPaquete():
    datos = request.json

    # Datos del origen
    localidad_origen = datos.get('LocalidadO')
    municipio_origen = datos.get('MunicipioO')
    entidad_origen = datos.get('EntidadO')

    # Datos del destino
    localidad_destino = datos.get('LocalidadD')
    municipio_destino = datos.get('MunicipioD')
    entidad_destino = datos.get('EntidadD')

    paquetes = datos.get('paquetes', [])
    print("Datos recibidos en Flask:", datos)

    db = get_session()
    try:
        stmt_origen = execute_query(localidad_origen, municipio_origen, entidad_origen)
        result_origen = db.execute(stmt_origen).first()

        if result_origen:
            latitud_origen = result_origen[4]
            longitud_origen = result_origen[5]
            print(latitud_origen)
            print(longitud_origen)

            try:
                stmt_destino = execute_query(localidad_destino, municipio_destino, entidad_destino)
                result_destino = db.execute(stmt_destino).first()

                if result_destino:
                    latitud_destino = result_destino[4]
                    longitud_destino = result_destino[5]
                    coords_1 = (float(latitud_origen), float(longitud_origen))
                    coords_2 = (float(latitud_destino), float(longitud_destino))
                    distancia = round(geodesic(coords_1, coords_2).kilometers, 2)

                    datos_distancia = calcularDistancia(distancia)

                    tarifa_base = 10
                    tarifa_total = 0
                    pesos_vm = []

                    # CORRECCIÓN: Procesar cada paquete correctamente
                    for paquete in paquetes:
                        largo = float(paquete['largo'])
                        ancho = float(paquete['ancho'])
                        alto = float(paquete['alto'])
                        peso_fisico = float(paquete['peso'])

                        # Calcular peso volumétrico de ESTE paquete
                        peso_vm = (largo * ancho * alto) / 6000
                        peso_vm_redondeado = round(peso_vm, 2)
                        pesos_vm.append(peso_vm_redondeado)

                        # CORRECCIÓN: Comparar el peso volumétrico de ESTE paquete con su peso físico
                        peso_max = max(peso_vm_redondeado, peso_fisico)
                        tarifa_total += tarifa_base * peso_max

                    # Agregar tarifa por distancia
                    tarifa_total += datos_distancia['tarifa']

                    print(f"Tarifa total: {tarifa_total}")
                    print(f"Fecha de entrega: {datos_distancia['fecha_entrega']}")

                    return jsonify({
                        "status": "success",
                        "tarifa": round(tarifa_total, 2),
                        "pesovm": pesos_vm,
                        "distancia": distancia,
                        "num_paquetes": len(paquetes),
                        "dias_entrega": datos_distancia['dias_entrega'],
                        "fecha_entrega": datos_distancia['fecha_entrega']
                    }), 200
                else:
                    return jsonify({
                        "status": "error",
                        "mensaje": "No se encontraron coordenadas para el destino"
                    }), 404

            except Exception as err:
                print(f"Error en destino: {err}")
                import traceback
                traceback.print_exc()  # Imprimir el stack trace completo
                return jsonify({"status": "error", "mensaje": str(err)}), 400
        else:
            return jsonify({
                "status": "error",
                "mensaje": "No se encontraron coordenadas para el origen"
            }), 404

    except Exception as err:
        print(f"Error general: {err}")
        import traceback
        traceback.print_exc()  # Imprimir el stack trace completo
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        db.close()
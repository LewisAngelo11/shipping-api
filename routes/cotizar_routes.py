# Endpoints de los metodos para cotizar envios

from flask import Blueprint, request, jsonify
from Database.conexion import obtener_conexion
from geopy.distance import geodesic   #libreria para posteriormente obtener distancias entre destino y origen de un paquete

cotizar_bp = Blueprint('cotizar', __name__)

# RECOMENDACIONES: Cambiar el nombre de la función ya que es ambiguo el actual y puede generar confusiones.
# Función para retornar los valores de Municipio y Estado con el codigo postal.
@cotizar_bp.route("/Cotizar/CP", methods=["POST"])
def Cotizar():
    conexion = obtener_conexion()
    datos = request.json
    CP = datos.get("CP")
    print("Datos recibidos en Flask:", datos)
    print(CP)
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500
    cursor = conexion.cursor(buffered= True)   #Se usa del buffer ya que es mas rapido la obtencion de los datos
    try:
        #Este es el query para obtener la cd,municipio,estado del cp que ingresamos
        cursor.execute("SELECT M.Nombre, EF.Nombre, L.NOM_LOC FROM paqueteria.codigos_postales CP "
                       "INNER JOIN paqueteria.municipio M ON CP.C_Estado = M.Id_EntidadFed AND CP.C_Mun = M.Id_Municipio "
                       "INNER JOIN paqueteria.entidad_federativa EF ON M.Id_EntidadFed = EF.Id_EntidadFed "
                       "INNER JOIN paqueteria.localidad L ON M.Id_EntidadFed = L.Id_EntidadFed AND M.Id_Municipio = L.Id_Municipio "
                       "WHERE CP.CP = %s", (CP,))

        # Obtén el primer registro en este caso la obtiene del buffer
        result = cursor.fetchone()

        if result:
            nombre_municipio = result[0]
            nombre_entidad_federativa = result[1]
            nombre_localidad = result[2]

            # Una vez acabado es obligatorio mandar una respuesta y en esta respuesta ponemos success como exitoso y los datos cd,mun,estado
            # todo se guarda en el json y en la seccion de this.authservice en el response de angular se recuperaran esos datos
            print(
                f"Municipio: {nombre_municipio}, Entidad Federativa: {nombre_entidad_federativa}, Localidad: {nombre_localidad}")

            return jsonify({"status": "success", "municipio": nombre_municipio, "entidad": nombre_entidad_federativa, "localidad": nombre_localidad}), 200
        else:
            return jsonify({"status": "error", "mensaje": "No se encontraron datos"}), 404

    except Exception as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()


# Función para cotizar un paquete
@cotizar_bp.route("/Cotizar/Paquete", methods=["POST"])
def CotizarPaquete():
    conexion = obtener_conexion()
    datos = request.json  # Obtiene los datos del archivo json de la papgina web
    print("Datos recibidos en Flask:", datos)
    PesoVM = (int(datos['Largo']) * int(datos['Ancho']) * int(datos['Alto']))/6000
    print(str(PesoVM))
    cursor = conexion.cursor(buffered = True)
    try:
        cursor.execute("SELECT L.Id_EntidadFed,L.Id_Municipio,L.Id_Localidad,L.NOM_LOC,L.LAT_DECIMAL,L.LON_DECIMAL FROM paqueteria.localidad L INNER JOIN paqueteria.municipio M ON M.Id_EntidadFed = L.Id_EntidadFed and M.Id_Municipio = L.Id_Municipio INNER JOIN paqueteria.entidad_federativa EF ON EF.Id_EntidadFed = M.Id_EntidadFed WHERE L.NOM_LOC = %s AND M.Nombre = %s AND EF.Nombre = %s;", (datos['LocalidadO'],datos['MunicipioO'],datos['EntidadO']))
        # Obtén el primer registro
        result = cursor.fetchone()
        if result:
            Latitud = result[4]
            longitud = result[5]
            print(Latitud)
            print(longitud)
            print()
            try:
                cursor.execute("SELECT L.Id_EntidadFed,L.Id_Municipio,L.Id_Localidad,L.NOM_LOC,L.LAT_DECIMAL,L.LON_DECIMAL FROM paqueteria.localidad L INNER JOIN paqueteria.municipio M ON M.Id_EntidadFed = L.Id_EntidadFed and M.Id_Municipio = L.Id_Municipio INNER JOIN paqueteria.entidad_federativa EF ON EF.Id_EntidadFed = M.Id_EntidadFed WHERE L.NOM_LOC = %s AND M.Nombre = %s AND EF.Nombre = %s;", (datos['LocalidadD'],datos['MunicipioD'],datos['EntidadD']))
                resultD = cursor.fetchone()
                tarifa = 0
                if resultD:
                    LatitudD = resultD[4]
                    longitudD = resultD[5]
                    coords_1 = (float(Latitud), float(longitud))  # Coordenadas de ejemplo (Empire State Building)
                    coords_2 = (float(LatitudD),float(longitudD))  # Coordenadas de ejemplo (Los Ángeles) distancia = geodesic(coords_1, coords_2).kilometers
                    distancia = geodesic(coords_1, coords_2).kilometers
                    print(distancia)
                    if(distancia) >= 200 and distancia <= 499:
                        tarifa = 150
                    elif distancia >=500 and distancia <= 799:
                        tarifa = 220
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
        cursor.close()
        conexion.close()
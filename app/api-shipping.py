import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from geopy.distance import geodesic   #libreria para posteriormente obtener distancias entre destino y origen de un paquete
import random

app = Flask(__name__)
CORS(app)  # Habilita CORS para todos los endpoints

# Configuración de conexión a MySQL
def obtener_conexion():
    try:
        return mysql.connector.connect(
            host="localhost", # IP del servidor donde se aloja la BD
            user="tu_usuario", # Usuario de la base de datos
            password="tu_constrasena", # Contraseña del usuario
            database="bd", # Nombre de la base de datos
            auth_plugin="mysql_native_password"  # Especificar el plugin
        )
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

# Funcion para validar el acceso a un usuario a la pagina
@app.route("/login", methods=["POST"])
def login():
    datos = request.json # Obtiene los datos del archivo json de la pagina web
    usuario = datos.get("Usuario") # Obtiene especificamente el Usuario
    contrasena = datos.get("Contrasena") # Obtiene especificamente la Contraseña
    print(f"Datos recibidos: Usuario= {usuario}, Contrasena= {contrasena}")

    conexion = obtener_conexion() # Obtener conexion a la BD
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    # Consulta para validar el usuario en la BD
    cursor.execute("SELECT * FROM usuario WHERE Usuario = %s AND Contrasena = %s", (usuario, contrasena))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        return jsonify({"status": "success", "rol": resultado.get("Rol", "Usuario")}), 200
    else:
        return jsonify({"status": "error", "mensaje": "Credenciales incorrectas"}), 401


# Funcion para crear un usuario a la base de datos
@app.route("/api/usuario", methods=["POST"])
def crear_usuario():
    usuario = request.json
    conexion = obtener_conexion() # Obtener conexion a la BD
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    print("Datos recibidos en Flask:", usuario)
    Name = usuario.get('Nombre')
    Apellido1 = usuario.get('Apellido1')
    Apellido2 = usuario.get('Apellido2')
    Fecha_Nac = usuario.get('Fecha_Nacimiento')
    Email = usuario.get('Email')
    Usuario = usuario.get('Usuario')
    Password = usuario.get('Contrasena')

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuario (Nombre, Apellido1, Apellido2, Fecha_Nacimiento, Email, Usuario, Contrasena) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (Name, Apellido1, Apellido2, Fecha_Nac, Email, Usuario, Password)
        )
        conexion.commit()
        return jsonify({"status": "success", "mensaje": "Usuario creado"}), 201
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

# Función para consultar un usuario a la BD.
@app.route("/usuario/consultar", methods=["POST"])
def consultar_usuario():
    datos = request.json  # Obtener el username de los parámetros de la URL
    conexion = obtener_conexion()
    print(datos)
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    try:
        # Realizamos la consulta para obtener la información del usuario
        cursor = conexion.cursor(buffered=True)
        cursor.execute("SELECT * FROM usuario WHERE Usuario = %s", (datos['username'],))
        usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if usuario:
            return jsonify({"status": "success", "username": usuario[1],"Apellido1": usuario[2],"Apellido2":usuario[3],"Fecha_Nacimiento":usuario[4],"Edad": usuario[5],"Email": usuario[6],"User": usuario[7],"Contraseña": usuario[8]}), 200
        else:
            return jsonify({"status": "error", "mensaje": "Usuario no encontrado"}), 404
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "mensaje": str(e)}), 500

# Función para actualizar el usuario a la BD
@app.route("/api/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):
    datos_actualizados = request.json
    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE usuario SET Usuario = %s, Contraseña = %s, Rol = %s WHERE id_Usuario = %s",
            (datos_actualizados['usuario'], datos_actualizados['contrasena'], datos_actualizados.get('Rol', 'Usuario'), id)
        )
        conexion.commit()
        return jsonify({"status": "success", "mensaje": "Usuario actualizado"}), 200
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

# Función para eliminar un usuario de la BD. En este servicio debe de ser DELETE, no POST.
@app.route('/eliminarUsers', methods=['POST'])
def eliminar_usuario():
    conexion = obtener_conexion()
    datos = request.json  # Obtiene los datos del archivo json de la página web
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM paqueteria.usuario WHERE contrasena = %s;",(datos['contraseña'],))

        conexion.commit()
        return jsonify(
            {"status": "success"}), 200
    except mysql.connector.Error as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

# Función para cotizar con el codigo postal.
@app.route("/Cotizar/CP", methods=["POST"])
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

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

# Función para cotizar un paquete
@app.route("/Cotizar/Paquete", methods=["POST"])
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
            except mysql.connector.Error as err:
                return jsonify({"status": "error", "mensaje": str(err)}), 400

            return jsonify({"status": "success","tarifa": str(tarifa), "pesovm": str(PesoVM), "distancia": str(distancia)}), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

# Función para realizar envios.
@app.route('/Cotizar/Envio', methods=['POST'])
def Envios():
    datos = request.json
    required_keys = ['Origen', 'Destino', 'Peso', 'Largo', 'Alto', 'Ancho', 'EmailR', 'EmailD']

    # Verificar si los atributos existen en los datos
    if not all(key in datos for key in required_keys):
        return jsonify({"status": "error", "mensaje": "Datos incompletos"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(buffered=True)

    try:
        # Insertar en Paquete
        cursor.execute("INSERT INTO Paquete (Peso, Estatus, Largo, Alto, Ancho) VALUES (%s, %s, %s, %s, %s);",
                       (datos['Peso'], 'EN PROCESO', datos['Largo'], datos['Alto'], datos['Ancho']))
        conexion.commit()

        # Obtener Id del remitente
        cursor.execute("SELECT id_Usuario FROM paqueteria.usuario WHERE Email = %s;", (datos['EmailR'],))
        Id_Remitente = cursor.fetchone()
        if not Id_Remitente:
            raise ValueError("Remitente no encontrado")
        Id_Remitente = Id_Remitente[0]

        # Obtener Id del destinatario
        cursor.execute("SELECT id_Usuario FROM paqueteria.usuario WHERE Email = %s;", (datos['EmailD'],))
        Id_Destinatario = cursor.fetchone()
        if not Id_Destinatario:
            raise ValueError("Destinatario no encontrado")
        Id_Destinatario = Id_Destinatario[0]

        # Obtener Id del paquete
        cursor.execute(
            "SELECT max(id_Paquete) FROM paqueteria.paquete WHERE Peso = %s and Largo = %s and Alto = %s and Ancho = %s;",
            (datos['Peso'], datos['Largo'], datos['Alto'], datos['Ancho']))
        Id_Paquete = cursor.fetchone()[0]

        # Insertar en Envio
        cursor.execute(
            "INSERT INTO envio(Fecha_Entrega, Costo, Origen, Destino, id_Paquete, id_Remitente, id_Destinatario, Estatus) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (datos['FechaR'], float(datos['tarifa'].replace('$', '')), datos['Origen'], datos['Destino'], Id_Paquete,
             Id_Remitente, Id_Destinatario, 'EN PROCESO'))
        conexion.commit()

        # Crear código de rastreo
        rastreo_code = ''.join([str(random.randint(0, 9)) for _ in range(20)])

        # Insertar en Rastreo
        cursor.execute(
            "SELECT max(id_Envio) FROM paqueteria.envio WHERE Fecha_Entrega = %s and Costo = %s and Origen = %s and Destino = %s and id_Paquete = %s and id_Remitente = %s and id_Destinatario = %s;",
            (datos['FechaR'], float(datos['tarifa'].replace('$', '')), datos['Origen'], datos['Destino'], Id_Paquete,
             Id_Remitente, Id_Destinatario))
        Id_Envio = cursor.fetchone()[0]
        cursor.execute("INSERT INTO rastreo(Codigo_Rastreo, id_Paquete, id_Envio) VALUES (%s, %s, %s);",
                       (rastreo_code, Id_Paquete, Id_Envio))
        conexion.commit()

    except mysql.connector.Error as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    except ValueError as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()

    return jsonify({"status": "success", "mensaje": "Datos procesados correctamente", "Rastreo_Code": rastreo_code}), 200

# Función para rastrear un envio con el código de rastreo
@app.route("/rastrear/rastreo", methods=["POST"])
def rastrear_envio():
    conexion = obtener_conexion()
    datos = request.json  # Obtiene los datos del archivo json de la página web
    rastreo = datos.get("Rastreo")
    print("Número de rastreo:", rastreo)  # Imprime solo el número de rastreo para depuración

    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    cursor = conexion.cursor()

    # Asegúrate de pasar el rastreo como una tupla y modificar la consulta SQL
    cursor.execute("""
        SELECT 
            e.id_Envio, 
            r.id_Paquete, 
            e.Estatus, 
            CONCAT(ur.Nombre, ' ', ur.Apellido1, ' ', ur.Apellido2) AS Remitente,
            CONCAT(ud.Nombre, ' ', ud.Apellido1, ' ', ud.Apellido2) AS Destinatario
        FROM 
            rastreo r
        JOIN 
            envio e ON r.id_Envio = e.id_Envio
        JOIN 
            usuario ur ON e.id_Remitente = ur.id_Usuario
        JOIN 
            usuario ud ON e.id_Destinatario = ud.id_Usuario
        WHERE 
            r.Codigo_Rastreo = %s
    """, (rastreo,))

    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        # Si el resultado se encuentra, devuelve los datos de manera estructurada
        return jsonify({
            "status": "success",
            "id_Envio": resultado[0],
            "id_Paquete": resultado[1],
            "Estatus": resultado[2],
            "Remitente": resultado[3],
            "Destinatario": resultado[4],

        }), 200
    return jsonify({"status": "error", "mensaje": "Numero de rastreo no encontrado"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
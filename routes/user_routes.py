# Endpoints de los metodos para los usuarios como consultar, actualizar y eliminar usuario
import jwt
from flask import Blueprint, request, jsonify
from Database.conexion import obtener_conexion
from config import JWT_SECRET  # la clave secreta del token

user_bp = Blueprint("users", __name__)

# CORREGIDO
# Función para consultar un usuario a la BD.
@user_bp.route("/usuario/consultar", methods=["GET"])
def consultar_usuario():
    token = request.headers.get("Authorization")  # Obtener el username de los parámetros de la URL
    if not token:
        return jsonify({"error": "Token no proporcionado"}), 401

    try:
        # Eliminar "Bearer " si está presente
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Extraer datos del payload
        usuario = payload.get("usuario")

        conexion = obtener_conexion()
        # Realizamos la consulta para obtener la información del usuario
        cursor = conexion.cursor(buffered=True)
        cursor.execute("SELECT * FROM usuario WHERE Usuario = %s", (usuario,))
        datos_usuario = cursor.fetchone()
        cursor.close()
        conexion.close()

        if datos_usuario:
            return jsonify({"status": "success", "Nombre": datos_usuario[1],"Apellido1": datos_usuario[2],"Apellido2": datos_usuario[3],"Fecha_Nacimiento": datos_usuario[4],"Edad": datos_usuario[5],"Email": datos_usuario[6],"User": datos_usuario[7]}), 200
        else:
            return jsonify({"status": "error", "mensaje": "Usuario no encontrado"}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401
    except Exception as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 500


# Función para actualizar el usuario a la BD
@user_bp.route("/api/usuarios/<int:id>", methods=["PUT"])
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
    except Exception as err:
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()


# CORRECIONES: El metodo http de esta función debe ser "DELETE" y no "POST. Ademas, debe tomar como parametro unico como el usuario o id"
# Función para eliminar un usuario de la BD.
@user_bp.route('/eliminarUsers', methods=['POST'])
def eliminar_usuario():
    conexion = obtener_conexion()
    datos = request.json  # Obtiene los datos del archivo json de la página web
    cursor = conexion.cursor()

    try:
        cursor.execute("DELETE FROM paqueteria.usuario WHERE contrasena = %s;",(datos['contraseña'],))

        conexion.commit()
        return jsonify(
            {"status": "success"}), 200
    except Exception as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 400
    finally:
        cursor.close()
        conexion.close()
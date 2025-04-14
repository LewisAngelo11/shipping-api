# Endpoints de los metodos para los usuarios como consultar, actualizar y eliminar usuario

from flask import Blueprint, request, jsonify
from Database.conexion import obtener_conexion

user_bp = Blueprint("users", __name__)

# CORRECIONES: el metodo http de esta función debe ser "GET" y no "POST".
# Función para consultar un usuario a la BD.
@user_bp.route("/usuario/consultar", methods=["POST"])
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
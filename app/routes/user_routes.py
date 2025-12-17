# Endpoints de los metodos para los usuarios como consultar, actualizar y eliminar usuario
import jwt
from datetime import date, datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import select, cast, String
from app.config.config import JWT_SECRET  # la clave secreta del token
from app.config.config_sqlalchemy import get_session
from app.models.usuario import Usuario
from app.models.envio import Envio
from app.models.rastreo import Rastreo

user_bp = Blueprint("users", __name__)

# CORREGIDO
# Función para consultar un usuario a la BD.
@user_bp.route("/usuario/consultar", methods=["GET"])
def consultar_usuario():
    token = request.headers.get("Authorization")  # Obtener el username de los parámetros de la URL
    if not token:
        return jsonify({"error": "Token no proporcionado"}), 401

    db = get_session()  # Obtener sesión SQLAlchemy
    try:
        # Eliminar "Bearer " si está presente
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Extraer datos del payload
        usuario = payload.get("usuario")
        print(usuario)

        datos_usuario = db.query(Usuario).filter_by(Usuario=usuario).first()

        # Devolver los datos del usuario al frontend
        if datos_usuario:
            return jsonify({
                "status": "success",
                "Nombre": datos_usuario.Nombre,
                "Apellido1": datos_usuario.Apellido1,
                "Apellido2": datos_usuario.Apellido2,
                "Fecha_Nacimiento": datos_usuario.Fecha_Nacimiento,
                "Telefono": datos_usuario.Telefono,
                "Edad": datos_usuario.Edad,
                "Email": datos_usuario.Email,
                "User": datos_usuario.Usuario
            }), 200
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
@user_bp.route("/usuario/actualizar", methods=["PATCH"])
def actualizar_usuario():
    token = request.headers.get("Authorization")  # Obtener el username de los parámetros de la URL
    if not token:
        return jsonify({"error": "Token no proporcionado"}), 401

    token_debug = token.split(" ")[1]
    print(f"Token recibido: {token}")  # Esto imprime el token en consola (para debug)

    db = get_session()  # Obtener sesión SQLAlchemy
    try:
        data = jwt.decode(token_debug, JWT_SECRET, algorithms=["HS256"])
        current_user_id = data['id']  # Obtiene el campo 'id' del token

        data = request.get_json()  # <- Este es el cuerpo con los nuevos valores (para debug)
        campos_validos = ["Nombre", "Apellido1", "Apellido2", "Email", "Usuario"]

        usuario = db.query(Usuario).filter_by(id_Usuario=current_user_id).first()
        if not usuario:
            return jsonify({'mensaje': 'Usuario no encontrado'}), 404

        for campo in campos_validos:
            if campo in data:
                setattr(usuario, campo, data[campo])

        # Imprimir los valores actualizados para debug (solo los campos válidos)
        print("Valores del usuario actualizados:")
        for campo in campos_validos:
            print(f"{campo}: {getattr(usuario, campo)}")

        # Guarda los datos en la BD
        db.commit()

        return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'mensaje': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'mensaje': 'Token inválido'}), 401
    except Exception as err:
        print(err)
        return jsonify({'mensaje': 'Error interno'}), 500


# Función para consultar el historial de envios hechos por el usuario
@user_bp.route("/usuario/historial", methods=["GET"])
def consultar_historial_envios():
    token = request.headers.get("Authorization")  # Obtener el username de los parámetros de la URL
    if not token:
        return jsonify({"error": "Token no proporcionado"}), 401

    db = get_session()  # Obtener sesión SQLAlchemy
    try:
        # Eliminar "Bearer " si está presente
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        # Extraer datos del payload
        id_usuario = payload.get("id")
        print(id_usuario)

        stmt = (
            select(
                Envio.Fecha_Entrega,
                Rastreo.Codigo_Rastreo,
                Envio.Origen,
                Envio.Destino,
                cast(Envio.Estatus, String).label("Estatus")
            )
            .join(
                Rastreo,
                Envio.id_Envio == Rastreo.id_Envio
            )
            .filter(
                Envio.id_Remitente == id_usuario
            )
        )

        result = db.execute(stmt).mappings().all()  # Ejecuta la query
        envios = []
        for row in result:
            row_dict = dict(row)

            # Convertir fechas a string YYYY-MM-DD
            for key in row_dict:
                if isinstance(row_dict[key], (date, datetime)):
                    row_dict[key] = row_dict[key].strftime("%Y-%m-%d")

            envios.append(row_dict)

        return jsonify(envios), 200

    except Exception as err:
        print(err)
        return jsonify({"status": "error", "mensaje": str(err)}), 500
    finally:
        db.close()
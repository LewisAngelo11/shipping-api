# Endpoints de los metodos de autenticación como el login y el crear_usuario

from flask import Blueprint, request, jsonify
from app.utils.password_utils import verificar_password, hash_password
from app.config.config_sqlalchemy import get_session
from app.models.usuario import Usuario
import jwt
import datetime
from app.config.config import JWT_SECRET

auth_bp = Blueprint("auth", __name__)

JWT_EXP_DELTA_SECONDS = 3600  # El token expirará en 1 hora

# ¡¡ENCRIPTACION AGREGADA!!
# Funcion para validar el acceso a un usuario a la pagina
@auth_bp.route("/login", methods=["POST"])
def login():
    datos = request.json # Obtiene los datos del archivo json de la pagina web
    usuario = datos.get("Usuario") # Obtiene especificamente el Usuario
    contrasena = datos.get("Contrasena") # Obtiene especificamente la Contraseña
    print(f"Datos recibidos: Usuario= {usuario}, Contrasena= {contrasena}")

    db = get_session()  # Obtener sesión SQLAlchemy
    try:
        usuario_encontrado = db.query(Usuario).filter(Usuario.Usuario == usuario).first()

        if usuario_encontrado:
            contrasena_guardada = usuario_encontrado.Contrasena # Esta contraseña será encriptada y comparada con la que esta en la BD que igualmente esta encriptada
            # Verificar la contraseña usando bcrypt
            if verificar_password(contrasena, contrasena_guardada): # Usar la funcion para encriptar la contraseña
                # Si la contraseña es correcta, generar el token JWT
                payload = {
                    "id": usuario_encontrado.id_Usuario,
                    "usuario": usuario,
                    "rol": getattr(usuario_encontrado, "Rol", "Usuario"),
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
                # Generar el token JWT
                token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

                # Devolver el token en la respuesta
                return jsonify({
                    "status": "success",
                    "rol": getattr(usuario_encontrado, "Rol", "Usuario"),
                    "token": token  # El token JWT se envía al cliente
                }), 200
        else:
            return jsonify({"status": "error", "mensaje": "Las credenciales son incorrectas"}), 401
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({"status": "error", "mensaje": "Error interno del servidor"}), 500
    finally:
        db.close()


# ¡¡ENCRIPTACION AGREGADA!!
# Funcion para crear un usuario a la base de datos
@auth_bp.route("/api/usuario", methods=["POST"])
def crear_usuario():
    datos = request.json

    print("Datos recibidos en Flask:", datos)
    # Crea el objeto Usuario para guardarlo a la BD
    nuevo_usuario = Usuario(
        Nombre=datos.get('Nombre'),
        Apellido1=datos.get('Apellido1'),
        Apellido2=datos.get('Apellido2'),
        Fecha_Nacimiento=datos.get('Fecha_Nacimiento'),
        Email=datos.get('Email'),
        Usuario=datos.get('Usuario'),
        Contrasena=hash_password(datos.get('Contrasena'))
    )

    session = get_session() # Obtener sesión SQLAlchemy

    try:
        session.add(nuevo_usuario) # Prepara el objeto Usuario antes de guardarlo a la BD
        session.commit() # Ejecuta los cambios pendientes en la BD
        return jsonify({"status": "success", "mensaje": "Usuario creado"}), 201
    except Exception as e:
        session.rollback()  # Revierte todos los cambios hechos en la transacción para evitar dejar la BD en un estado inconsistente.
        return jsonify({"status": "error", "mensaje": str(e)}), 400
    finally:
        session.close() # Cierra la sesión SQLAlchemy para liberar los recursos

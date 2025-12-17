# Endpoints de los metodos de autenticación como el login y el crear_usuario

from flask import Blueprint, request, jsonify
from app.utils.password_utils import verificar_password, hash_password
from app.config.config_sqlalchemy import get_session
from app.models.usuario import Usuario
import jwt
import datetime
from app.config.config import JWT_SECRET
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config.config import (
    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS,
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
)

auth_bp = Blueprint("auth", __name__)

JWT_EXP_DELTA_SECONDS = 3600  # El token expirará en 1 hora

# ¡¡ENCRIPTACION AGREGADA!!
# Funcion para validar el acceso a un usuario a la pagina
@auth_bp.route("/login", methods=["POST"])
def login():
    datos = request.json  # Obtiene los datos del archivo json de la pagina web
    usuario = datos.get("Usuario")  # Obtiene especificamente el Usuario
    contrasena = datos.get("Contrasena")  # Obtiene especificamente la Contraseña

    db = get_session()  # Obtener sesión SQLAlchemy
    try:
        usuario_encontrado = db.query(Usuario).filter(Usuario.Usuario == usuario).first()

        if usuario_encontrado:
            contrasena_guardada = usuario_encontrado.Contrasena  # Esta contraseña será encriptada y comparada con la que esta en la BD que igualmente esta encriptada
            # Verificar la contraseña usando bcrypt
            if verificar_password(contrasena, contrasena_guardada):  # Usar la funcion para encriptar la contraseña
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
                # Contraseña incorrecta
                return jsonify({"status": "error", "mensaje": "Contraseña incorrecta"}), 401
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
        Telefono=datos.get('Telefono'),
        Email=datos.get('Email'),
        Usuario=datos.get('Usuario'),
        Contrasena=hash_password(datos.get('Contrasena'))
    )

    session = get_session()  # Obtener sesión SQLAlchemy

    try:
        session.add(nuevo_usuario)  # Prepara el objeto Usuario antes de guardarlo a la BD
        session.commit()  # Ejecuta los cambios pendientes en la BD
        return jsonify({"status": "success", "mensaje": "Usuario creado"}), 201
    except Exception as e:
        session.rollback()  # Revierte todos los cambios hechos en la transacción para evitar dejar la BD en un estado inconsistente.
        return jsonify({"status": "error", "mensaje": str(e)}), 400
    finally:
        session.close()  # Cierra la sesión SQLAlchemy para liberar los recursos


# Endpoint para verificar si un email existe en la BD
@auth_bp.route("/usuario/verificar-email", methods=["POST"])
def verificar_email():
    datos = request.json
    email = datos.get("Email")

    if not email:
        return jsonify({
            "status": "error",
            "existe": False,
            "mensaje": "Email es requerido"
        }), 400

    db = get_session()
    try:
        # Buscar usuario por email
        usuario_encontrado = db.query(Usuario).filter(Usuario.Email == email).first()

        if usuario_encontrado:
            return jsonify({
                "status": "success",
                "existe": True,
                "mensaje": "Email encontrado"
            }), 200
        else:
            return jsonify({
                "status": "success",
                "existe": False,
                "mensaje": "Email no encontrado"
            }), 200

    except Exception as e:
        print(f"Error al verificar email: {e}")
        return jsonify({
            "status": "error",
            "existe": False,
            "mensaje": "Error interno del servidor"
        }), 500
    finally:
        db.close()


# ¡¡ENCRIPTACION AGREGADA!!
# Endpoint para cambiar contraseña
@auth_bp.route("/usuario/cambiar", methods=["PUT"])
def cambiar_contrasena():
    datos = request.json
    email = datos.get("Email")
    nueva_contrasena = datos.get("NuevaContrasena")

    print(f"Solicitud de cambio de contraseña para: {email}")

    # Validar que se enviaron los datos necesarios
    if not email or not nueva_contrasena:
        return jsonify({
            "status": "error",
            "mensaje": "Email y nueva contraseña son requeridos"
        }), 400

    db = get_session()
    try:
        # Buscar el usuario por email
        usuario_encontrado = db.query(Usuario).filter(Usuario.Email == email).first()

        if not usuario_encontrado:
            return jsonify({
                "status": "error",
                "mensaje": "No se encontró ningún usuario con ese correo electrónico"
            }), 404

        # Hash de la nueva contraseña usando bcrypt
        nueva_contrasena_hash = hash_password(nueva_contrasena)

        # Actualizar la contraseña del usuario
        usuario_encontrado.Contrasena = nueva_contrasena_hash

        # Guardar cambios en la base de datos
        db.commit()

        print(f"Contraseña actualizada exitosamente para: {email}")

        return jsonify({
            "status": "success",
            "mensaje": "Contraseña actualizada correctamente"
        }), 200

    except Exception as e:
        db.rollback()
        print(f"Error al cambiar contraseña: {e}")
        return jsonify({
            "status": "error",
            "mensaje": "Error interno del servidor"
        }), 500
    finally:
        db.close()


# SISTEMA DE RECUPERACIÓN POR EMAIL

# Diccionario temporal para guardar códigos
codigos_recuperacion = {}

def generar_codigo():
    """Genera un código de 6 dígitos"""
    return ''.join(random.choices(string.digits, k=6))


def enviar_email(destinatario, asunto, cuerpo_html):
    """Envía un email usando Gmail SMTP"""
    try:
        # Crear mensaje
        mensaje = MIMEMultipart('alternative')
        mensaje['Subject'] = asunto
        mensaje['From'] = MAIL_DEFAULT_SENDER
        mensaje['To'] = destinatario

        # Adjuntar HTML
        parte_html = MIMEText(cuerpo_html, 'html')
        mensaje.attach(parte_html)

        # Conectar y enviar
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(mensaje)

        print(f"Email enviado exitosamente a {destinatario}")
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False


@auth_bp.route("/usuario/solicitar-codigo", methods=["POST"])
def solicitar_codigo_recuperacion():
    """
    Genera un código de 6 dígitos y lo envía por email
    """
    datos = request.json
    email = datos.get("Email")

    if not email:
        return jsonify({
            "status": "error",
            "mensaje": "Email es requerido"
        }), 400

    db = get_session()
    try:
        # Verificar que el email existe
        usuario = db.query(Usuario).filter(Usuario.Email == email).first()

        if not usuario:
            return jsonify({
                "status": "error",
                "mensaje": "No existe una cuenta con este correo electrónico"
            }), 404

        # Generar código de 6 dígitos
        codigo = generar_codigo()

        # Guardar código con timestamp (expira en 15 minutos)
        codigos_recuperacion[email] = {
            'codigo': codigo,
            'timestamp': datetime.datetime.now()
        }

        # Crear HTML del email
        cuerpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 50px auto;
                    background-color: #ffffff;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #e64d11 0%, #d43d01 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                    text-align: center;
                }}
                .code-box {{
                    background-color: #f9f9f9;
                    border: 2px dashed #e64d11;
                    border-radius: 10px;
                    padding: 20px;
                    margin: 30px 0;
                    display: inline-block;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    letter-spacing: 8px;
                    color: #1c1c1c;
                    font-family: 'Courier New', monospace;
                }}
                .footer {{
                    background-color: #f4f4f4;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .warning {{
                    color: #e64d11;
                    font-size: 14px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recuperación de Contraseña</h1>
                    <p>Tu Paquetería de Confianza</p>
                </div>
                <div class="content">
                    <h2>Hola, {usuario.Nombre}</h2>
                    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
                    <p>Usa el siguiente código de verificación:</p>

                    <div class="code-box">
                        <div class="code">{codigo}</div>
                    </div>

                    <p class="warning">Este código expirará en 15 minutos</p>
                    <p style="color: #666; font-size: 14px; margin-top: 30px;">
                        Si no solicitaste este cambio, ignora este correo.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2024 Paquetería Express | Todos los derechos reservados</p>
                    <p>Este es un correo automático, por favor no respondas a este mensaje</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Enviar email
        email_enviado = enviar_email(
            email,
            "Código de Recuperación - Paquetería Express",
            cuerpo_html
        )

        if email_enviado:
            return jsonify({
                "status": "success",
                "mensaje": "Código enviado correctamente"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "mensaje": "Error al enviar el correo electrónico"
            }), 500

    except Exception as e:
        print(f"Error al solicitar código: {e}")
        return jsonify({
            "status": "error",
            "mensaje": "Error interno del servidor"
        }), 500
    finally:
        db.close()


@auth_bp.route("/usuario/validar-codigo", methods=["POST"])
def validar_codigo_solo():
    """
    Valida el código de 6 dígitos SIN consumirlo ni cambiar la contraseña
    Esto permite verificar el código antes de pedir la nueva contraseña
    """
    datos = request.json
    email = datos.get("Email")
    codigo = datos.get("Codigo")

    if not email or not codigo:
        return jsonify({
            "status": "error",
            "mensaje": "Email y código son requeridos"
        }), 400

    # Verificar si existe un código para ese email
    if email not in codigos_recuperacion:
        return jsonify({
            "status": "error",
            "mensaje": "Código inválido o expirado"
        }), 400

    codigo_data = codigos_recuperacion[email]

    # Verificar si el código expiró (15 minutos)
    tiempo_transcurrido = datetime.datetime.now() - codigo_data['timestamp']
    if tiempo_transcurrido.total_seconds() > 900:  # 15 minutos = 900 segundos
        del codigos_recuperacion[email]
        return jsonify({
            "status": "error",
            "mensaje": "El código ha expirado. Solicita uno nuevo"
        }), 400

    # Verificar que el código coincida
    if codigo_data['codigo'] != codigo:
        return jsonify({
            "status": "error",
            "mensaje": "Código incorrecto"
        }), 400

    # Código válido! NO lo eliminamos, solo confirmamos que es correcto
    return jsonify({
        "status": "success",
        "mensaje": "Código válido"
    }), 200


@auth_bp.route("/usuario/verificar-codigo", methods=["POST"])
def verificar_codigo_y_cambiar():
    """
    Verifica el código de 6 dígitos y cambia la contraseña
    """
    datos = request.json
    email = datos.get("Email")
    codigo = datos.get("Codigo")
    nueva_contrasena = datos.get("NuevaContrasena")

    if not email or not codigo or not nueva_contrasena:
        return jsonify({
            "status": "error",
            "mensaje": "Email, código y nueva contraseña son requeridos"
        }), 400

    # Verificar si existe un código para ese email
    if email not in codigos_recuperacion:
        return jsonify({
            "status": "error",
            "mensaje": "Código inválido o expirado"
        }), 400

    codigo_data = codigos_recuperacion[email]

    # Verificar si el código expiró (15 minutos)
    tiempo_transcurrido = datetime.datetime.now() - codigo_data['timestamp']
    if tiempo_transcurrido.total_seconds() > 900:  # 15 minutos = 900 segundos
        del codigos_recuperacion[email]
        return jsonify({
            "status": "error",
            "mensaje": "El código ha expirado. Solicita uno nuevo"
        }), 400

    # Verificar que el código coincida
    if codigo_data['codigo'] != codigo:
        return jsonify({
            "status": "error",
            "mensaje": "Código incorrecto"
        }), 400

    # Código válido, proceder a cambiar la contraseña
    db = get_session()
    try:
        usuario = db.query(Usuario).filter(Usuario.Email == email).first()

        if not usuario:
            return jsonify({
                "status": "error",
                "mensaje": "Usuario no encontrado"
            }), 404

        # Actualizar contraseña
        usuario.Contrasena = hash_password(nueva_contrasena)
        db.commit()

        # Eliminar el código usado
        del codigos_recuperacion[email]

        print(f"Contraseña actualizada exitosamente para: {email}")

        return jsonify({
            "status": "success",
            "mensaje": "Contraseña actualizada correctamente"
        }), 200

    except Exception as e:
        db.rollback()
        print(f"Error al cambiar contraseña: {e}")
        return jsonify({
            "status": "error",
            "mensaje": "Error interno del servidor"
        }), 500
    finally:
        db.close()
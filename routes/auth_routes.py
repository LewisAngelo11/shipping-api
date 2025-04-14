# Endpoints de los metodos de autenticación como el login y el crear_usuario

from flask import Blueprint, request, jsonify
from Database.conexion import obtener_conexion
from utils.password_utils import verificar_password, hash_password
import jwt
import datetime
from config import JWT_SECRET

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

    conexion = obtener_conexion() # Obtener conexion a la BD
    if not conexion:
        return jsonify({"status": "error", "mensaje": "Error de conexión con la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    # Consulta para validar el usuario en la BD
    cursor.execute("SELECT * FROM usuario WHERE Usuario = %s", (usuario,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()

    if resultado:
        contrasena_guardada = resultado["Contrasena"] # Esta contraseña será encriptada y comparada con la que esta en la BD que igualmente esta encriptada
        # Verificar la contraseña usando bcrypt
        if verificar_password(contrasena, contrasena_guardada): # Usar la funcion para encriptar la contraseña
            # Si la contraseña es correcta, generar el token JWT
            payload = {
                "usuario": usuario,
                "rol": resultado.get("Rol", "Usuario"),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
            }
            # Generar el token JWT
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

            # Devolver el token en la respuesta
            return jsonify({
                "status": "success",
                "rol": resultado.get("Rol", "Usuario"),
                "token": token  # El token JWT se envía al cliente
            }), 200
    else:
        return jsonify({"status": "error", "mensaje": "Las credenciales son incorrectas"}), 401


# ¡¡ENCRIPTACION AGREGADA!!
# Funcion para crear un usuario a la base de datos
@auth_bp.route("/api/usuario", methods=["POST"])
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

    # Hashear la contraseña antes de guardarla a la BD
    Password_hash = hash_password(Password)

    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuario (Nombre, Apellido1, Apellido2, Fecha_Nacimiento, Email, Usuario, Contrasena) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (Name, Apellido1, Apellido2, Fecha_Nac, Email, Usuario, Password_hash)
        )
        conexion.commit()
        return jsonify({"status": "success", "mensaje": "Usuario creado"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400
    finally:
        cursor.close()
        conexion.close()
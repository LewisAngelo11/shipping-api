import os

# Configuración para MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario',
    'password': 'tu_password',
    'database': 'tu_base_de_datos'
}

# Clave secreta para JWT (Aún no integrado el token)
JWT_SECRET = os.getenv("JWT_SECRET", "clave_secreta")
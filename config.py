import os

# Configuración para MySQL
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario',
    'password': 'tu_contraseña',
    'database': 'tu_base_datos'
}

# Clave secreta para JWT (Aún no integrado el token)
JWT_SECRET = os.getenv("JWT_SECRET", "j35Fh$99!ad8$#G6@kL#1Pz!232$#")
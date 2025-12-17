import os

# Datos de conexión a MySQL
DB_USER = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "your_host"
DB_NAME = "paqueteria"

# URI para SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Clave secreta para JWT (Integrado y funcional pero no definitivo)
JWT_SECRET = os.getenv("JWT_SECRET", "j35Fh$99!ad8$#G6@kL#1Pz!232$#")

# Configuración de Email para recuperación de contraseña
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "cotabuelnaandresruben@gmail.com"  # Cambiar por tu email
MAIL_PASSWORD = "ihru jnob shqw zljt"  # Tu contraseña de aplicación de Gmail
MAIL_DEFAULT_SENDER = "cotabuelnaandresruben@gmail.com"  # Cambiar por tu email

# Otras configuraciones
SQLALCHEMY_TRACK_MODIFICATIONS = False
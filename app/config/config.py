import os

# Datos de conexión a MySQL
DB_USER = "your_user"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_NAME = "your_data_base"

# URI para SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Clave secreta para JWT (Integrado y funcional pero no definitivo)
JWT_SECRET = os.getenv("JWT_SECRET", "j35Fh$99!ad8$#G6@kL#1Pz!232$#")

# Otras configuraciones
SQLALCHEMY_TRACK_MODIFICATIONS = False
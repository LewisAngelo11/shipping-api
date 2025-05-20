from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import SQLALCHEMY_DATABASE_URI  # Importa la URI desde config.py

# Crear la base para los modelos de SQLAlchemy
Base = declarative_base()

# Crear el engine para SQLAlchemy usando la URI de config.py
engine = create_engine(SQLALCHEMY_DATABASE_URI)

# Configuración de la sesión
Session = sessionmaker(bind=engine)

# Función para obtener una nueva sesión
def get_session():
    return Session()
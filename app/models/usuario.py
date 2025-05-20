from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class Usuario(Base):
    __tablename__ = 'usuario'

    id_Usuario = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(50))
    Apellido1 = Column(String(30))
    Apellido2 = Column(String(30))
    Fecha_Nacimiento = Column(Date)
    Edad = Column(Integer)
    Email = Column(String(50))
    Usuario = Column(String(30))
    Contrasena = Column(String(100))

    def __repr__(self):
        return f"<Usuario(id={self.id_Usuario}, Usuario='{self.Usuario}')>"
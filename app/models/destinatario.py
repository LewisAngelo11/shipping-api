from sqlalchemy import Column, Integer, String
from app.config.config_sqlalchemy import Base

class Destinatario(Base):
    __tablename__ = 'destinatario'

    id_Destinatario = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(50))
    Apellido1 = Column(String(30))
    Apellido2 = Column(String(30))
    Email = Column(String(50), unique=True)
    Telefono = Column(String(15))

    def __repr__(self):
        return f"<Destinatario(id={self.id_Destinatario}, Nombre={self.Nombre} {self.Apellido1}, Email={self.Email})>"
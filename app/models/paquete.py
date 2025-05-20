from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class Paquete(Base):
    __tablename__ = 'paquete'

    # Definimos las columnas
    id_Paquete = Column(Integer, primary_key=True, autoincrement=True)
    Guia = Column(String(18), nullable=True)
    Peso = Column(DECIMAL(16, 2), nullable=True)
    Largo = Column(DECIMAL(16, 2), nullable=True)
    Alto = Column(DECIMAL(16, 2), nullable=True)
    Ancho = Column(DECIMAL(16, 2), nullable=True)


    def __repr__(self):
        return f"<Paquete(id_Paquete={self.id_Paquete}, Guia={self.Guia})>"
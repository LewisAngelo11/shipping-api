from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class Rastreo(Base):
    __tablename__ = 'rastreo'

    # Definimos las columnas
    Codigo_Rastreo = Column(String(20), primary_key=True)
    id_Paquete = Column(Integer, ForeignKey('paquete.id_Paquete'), nullable=True)
    id_Envio = Column(Integer, ForeignKey('envio.id_Envio'), nullable=True)

    # Relación con envio
    envio = relationship('Envio', primaryjoin="Rastreo.id_Envio == Envio.id_Envio")

    # Relación con Paquete (un rastreo está asociado a un paquete)
    paquete = relationship('Paquete', primaryjoin="Rastreo.id_Paquete == Paquete.id_Paquete")

    def __repr__(self):
        return f"<Rastreo(Codigo_Rastreo={self.Codigo_Rastreo}, id_Paquete={self.id_Paquete}, id_Envio={self.id_Envio})>"
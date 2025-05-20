from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class Municipio(Base):
    __tablename__ = 'municipio'
    __table_args__ = {'schema': 'paqueteria'}

    Id_EntidadFed = Column(Integer, ForeignKey('paqueteria.entidad_federativa.Id_EntidadFed'), primary_key=True)
    Id_Municipio = Column(Integer, primary_key=True)
    Nombre = Column(String(100), nullable=False)
    CVE_CAB = Column(String(45), nullable=True)
    POB_TOTAL = Column(String(45), nullable=True)
    POB_MASCULINA = Column(String(45), nullable=True)
    POB_FEMENINA = Column(String(45), nullable=True)
    TOTAL_DE_VIVIENDAS_HABITADAS = Column(String(45), nullable=True)

    entidad_fed = relationship('EntidadFederativa', foreign_keys=[Id_EntidadFed])

    def __repr__(self):
        return f"<Municipio(Id_Municipio={self.Id_Municipio}, Nombre={self.Nombre})>"
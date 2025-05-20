from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class Localidad(Base):
    __tablename__ = 'localidad'
    __table_args__ = {'schema': 'paqueteria'}

    Id_EntidadFed = Column(Integer, ForeignKey('paqueteria.municipio.Id_EntidadFed'), primary_key=True)
    Id_Municipio = Column(Integer, ForeignKey('paqueteria.municipio.Id_Municipio'), primary_key=True)
    Id_Localidad = Column(Integer, primary_key=True)
    NOM_LOC = Column(String(100), nullable=False)
    AMBITO = Column(String(45), nullable=True)
    LATITUD = Column(String(45), nullable=True)
    LONGITUD = Column(String(45), nullable=True)
    LAT_DECIMAL = Column(String(45), nullable=True)
    LON_DECIMAL = Column(String(45), nullable=True)
    ALTITUD = Column(String(45), nullable=True)
    CVE_CARTA = Column(String(45), nullable=True)
    POB_TOTAL = Column(String(45), nullable=True)
    POB_MASCULINA = Column(String(45), nullable=True)
    POB_FEMENINA = Column(String(45), nullable=True)
    TOTAL_DE_VIVIENDAS_HABITADAS = Column(String(45), nullable=True)

    # Modificación en las relaciones para usar join conditions
    municipio = relationship('Municipio', foreign_keys=[Id_Municipio, Id_EntidadFed],
                            primaryjoin="and_(Localidad.Id_Municipio==Municipio.Id_Municipio, "
                                       "Localidad.Id_EntidadFed==Municipio.Id_EntidadFed)")

    def __repr__(self):
        return f"<Localidad(Id_Localidad={self.Id_Localidad}, NOM_LOC={self.NOM_LOC})>"
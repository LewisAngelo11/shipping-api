from sqlalchemy import Column, Integer, String
from app.config.config_sqlalchemy import Base

class EntidadFederativa(Base):
    __tablename__ = 'entidad_federativa'
    __table_args__ = {'schema': 'paqueteria'}

    Id_EntidadFed = Column(Integer, primary_key=True)
    Nombre = Column(String(40), nullable=False)
    Nombre_ABRV = Column(String(8), nullable=False)
    Pob_Total = Column(String(10), nullable=False)
    POB_MASCULINA = Column(String(10), nullable=False)
    POB_FEMENINA = Column(String(10), nullable=False)
    TOTAL_DE_VIVIENDAS = Column(String(10), nullable=False)

    def __repr__(self):
        return f"<EntidadFederativa(Id_EntidadFed={self.Id_EntidadFed}, Nombre={self.Nombre})>"
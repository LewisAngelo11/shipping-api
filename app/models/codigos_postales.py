from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base

class CodigosPostales(Base):
    __tablename__ = 'codigos_postales'
    __table_args__ = (
        ForeignKeyConstraint(
            ['C_Estado', 'C_Mun'],
            ['paqueteria.municipio.Id_EntidadFed', 'paqueteria.municipio.Id_Municipio']
        ),
        {'schema': 'paqueteria'}
    )

    Id = Column(Integer, primary_key=True, autoincrement=True)
    CP = Column(String(5), nullable=True)
    Asentamiento = Column(String(45), nullable=True)
    Tipo_Asentamiento = Column(String(40), nullable=True)
    C_Estado = Column(Integer, nullable=True)
    C_Mun = Column(Integer, nullable=True)
    D_CP = Column(String(45), nullable=True)
    C_Oficina = Column(String(45), nullable=True)
    C_Tipo_Asen = Column(String(45), nullable=True)
    id_asenta_cpcons = Column(String(45), nullable=True)
    d_zona = Column(String(45), nullable=True)
    c_cve_ciudad = Column(String(45), nullable=True)

    # Relación con `Municipio` utilizando primaryjoin
    municipio = relationship('Municipio',
                           primaryjoin="and_(CodigosPostales.C_Estado==Municipio.Id_EntidadFed, "
                                      "CodigosPostales.C_Mun==Municipio.Id_Municipio)")

    def __repr__(self):
        return f"<CodigosPostales(Id={self.Id}, CP={self.CP})>"
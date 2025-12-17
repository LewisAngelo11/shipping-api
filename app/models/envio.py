from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Double
from sqlalchemy.orm import relationship
from app.config.config_sqlalchemy import Base
from enum import Enum as PyEnum

class EstatusEnvio(PyEnum):
    EN_PROCESO = "EN PROCESO"
    ENVIADO = "ENVIADO"
    EN_ENTREGA_A_DOMICILIO = "EN ENTREGA A DOMICILIO"
    ENTREGADO = "ENTREGADO"

class Envio(Base):
    __tablename__ = 'envio'

    id_Envio = Column(Integer, primary_key=True, autoincrement=True)
    Fecha_Envio = Column(Date, nullable=True)
    Fecha_Entrega = Column(Date, nullable=True)
    Costo = Column(Double, nullable=True)  # Cambiado a Double para soportar decimales
    Origen = Column(String(70), nullable=True)
    Direccion_Origen = Column(String(150))
    Destino = Column(String(70), nullable=True)
    Direccion_Destino = Column(String(150))
    id_Remitente = Column(Integer, ForeignKey('usuario.id_Usuario'), nullable=True)
    id_Destinatario = Column(Integer, ForeignKey('destinatario.id_Destinatario'), nullable=True)  # ✨ CAMBIO AQUÍ
    Estatus = Column(
        Enum(EstatusEnvio, native_enum=False, values_callable=lambda enum: [e.value for e in enum]),
        nullable=True
    )

    # Relación con Usuario como remitente
    remitente = relationship('Usuario', foreign_keys=[id_Remitente])
    # Relación con Destinatario
    destinatario = relationship('Destinatario', foreign_keys=[id_Destinatario])

    def __repr__(self):
        return f"<Envio(id_Envio={self.id_Envio}, Estatus={self.Estatus})>"
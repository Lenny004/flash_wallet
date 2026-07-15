from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, Date, Time

from app.db.base import Base


class Transaccion(Base):
    """Transacción de pago de un servicio con una tarjeta (tabla tbtransaccion)."""

    __tablename__ = "tbtransaccion"

    id_transaccion = Column(Integer, primary_key=True, autoincrement=True, index=True)
    fecha_transaccion = Column(Date, nullable=False)
    hora_transaccion = Column(Time, nullable=False)
    monto = Column(DECIMAL(7, 2), nullable=False)
    frecuencia = Column(Integer, nullable=False)
    descripcion = Column(String(40), nullable=False)
    id_tarjeta = Column(Integer, ForeignKey("tbtarjeta_digital.id_tarjeta"), nullable=False)
    id_servicio = Column(Integer, ForeignKey("tbservicios.id_servicio"), nullable=False)
    id_estado = Column(Integer, ForeignKey("tbestado.id_estado"), nullable=False)

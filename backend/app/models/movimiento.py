from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, DECIMAL

from app.db.base import Base


class Movimiento(Base):
    """Movimiento de saldo en una tarjeta digital (tabla tbmovimiento)."""

    __tablename__ = "tbmovimiento"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_tarjeta = Column(Integer, ForeignKey("tbtarjeta_digital.id_tarjeta"), nullable=False)
    tipo = Column(String(20), nullable=False)
    monto = Column(DECIMAL(10, 2), nullable=False)
    saldo_anterior = Column(DECIMAL(10, 2), nullable=False)
    saldo_nuevo = Column(DECIMAL(10, 2), nullable=False)
    referencia = Column(String(80), nullable=True)
    creado_en = Column(DateTime, nullable=False)

from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, Date, Time

from app.db.base import Base


class Historial(Base):
    """Registro de depósito/recarga en una tarjeta digital (tabla tbhistorial)."""

    __tablename__ = "tbhistorial"

    id_historial = Column(Integer, primary_key=True, autoincrement=True, index=True)
    monto_agregado = Column(DECIMAL(7, 2), nullable=False)
    fecha_historial = Column(Date, nullable=False)
    hora_historial = Column(Time, nullable=False)
    id_tarjeta = Column(Integer, ForeignKey("tbtarjeta_digital.id_tarjeta"), nullable=False)

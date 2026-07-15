from sqlalchemy import Column, ForeignKey, Integer, DECIMAL, Date, Time

from app.db.base import Base


class Factura(Base):
    """Factura generada a partir de una transacción completada (tabla tbfactura)."""

    __tablename__ = "tbfactura"

    id_factura = Column(Integer, primary_key=True, autoincrement=True, index=True)
    monto_total = Column(DECIMAL(6, 2), nullable=False)
    fecha_factura = Column(Date, nullable=False)
    hora_factura = Column(Time, nullable=False)
    id_transaccion = Column(Integer, ForeignKey("tbtransaccion.id_transaccion"), nullable=False)

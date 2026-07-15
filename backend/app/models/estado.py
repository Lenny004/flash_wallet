from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Estado(Base):
    """Estado de una transacción de pago (tabla tbestado)."""

    __tablename__ = "tbestado"

    id_estado = Column(Integer, primary_key=True, autoincrement=True, index=True)
    estado = Column(String(10), nullable=False)

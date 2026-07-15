from sqlalchemy import Column, Integer, String, Date, DECIMAL

from app.db.base import Base


class Tarjeta(Base):
    __tablename__ = "tbtarjeta_digital"

    id_tarjeta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pan = Column(String(19), nullable=False)
    cvc = Column(Integer, nullable=False)
    balance = Column(DECIMAL(7, 2), nullable=False)
    fecha_creacion = Column(Date, nullable=False)
    fecha_actualizacion = Column(Date, nullable=False)
    id_usuario = Column(String(50), unique=True, nullable=False)

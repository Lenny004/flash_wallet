from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Servicio(Base):
    __tablename__ = "tbservicios"

    id_servicio = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(30), nullable=False, unique=True)
    img_servicio = Column(String(100), nullable=False)

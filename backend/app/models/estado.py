from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Estado(Base):
    __tablename__ = "tbestado"

    id_estado = Column(Integer, primary_key=True, autoincrement=True, index=True)
    estado = Column(String(10), nullable=False)

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Definir la clase base para SQLAlchemy
Base = declarative_base()

class Estado(Base):
    __tablename__ = "tbestado"

    id_estado = Column(Integer, primary_key=True, autoincrement=True, index=True)
    estado = Column(String(10), nullable=False)

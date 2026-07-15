from sqlalchemy import Column, Integer, String, Date, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Definir la clase base para SQLAlchemy
Base = declarative_base()

class Tarjeta(Base):
    __tablename__ = "tbtarjeta_digital"
    
    id_tarjeta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pan = Column(String(19), nullable=False)
    cvc = Column(Integer, nullable=False) 
    balance = Column(DECIMAL(7, 2), nullable=False)
    fecha_creacion = Column(Date, nullable=False) 
    fecha_actualizacion = Column(Date, nullable=False)
    id_usuario = Column(String(50), unique=True, nullable=False)
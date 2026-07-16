from sqlalchemy import Column, Integer, String, DECIMAL, Date, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Transaccion(Base):
    __tablename__ = "tbtransaccion"  
    
    id_transaccion = Column(Integer, primary_key=True, autoincrement=True, index=True)
    fecha_transaccion = Column(Date, nullable=False)
    hora_transaccion = Column(Time, nullable=False)
    monto = Column(DECIMAL(7, 2), nullable=False)
    frecuencia = Column(Integer, nullable=False)
    descripcion = Column(String(40), nullable=False)
    id_tarjeta = Column(Integer, nullable=False)
    id_servicio = Column(Integer, nullable=False)
    id_estado = Column(Integer, nullable=False)

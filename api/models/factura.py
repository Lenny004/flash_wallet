from sqlalchemy import Column, Integer, DECIMAL, Date, Time
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Factura(Base):
    __tablename__ = "tbfactura"
    
    id_factura = Column(Integer, primary_key=True, autoincrement=True, index=True)
    monto_total = Column(DECIMAL(6, 2), nullable=False)
    fecha_factura = Column(Date, nullable=False)
    hora_factura = Column(Time, nullable=False)
    id_transaccion = Column(Integer, nullable=False)

from sqlalchemy import Column, Integer, String, DECIMAL, Date, Time
from sqlalchemy.ext.declarative import declarative_base

# Definir la clase base para SQLAlchemy
Base = declarative_base()

class Historial(Base):
    __tablename__ = "tbhistorial"  # Nombre de la tabla en la base de datos
    
    id_historial = Column(Integer, primary_key=True, autoincrement=True, index=True)
    monto_agregado = Column(DECIMAL(7, 2), nullable=False)  # DECIMAL(7, 2) para manejar montos con 2 decimales
    fecha_historial = Column(Date, nullable=False)  # Almacenamos solo la fecha
    hora_historial = Column(Time, nullable=False)  # Almacenamos solo la hora
    id_tarjeta = Column(Integer, nullable=False)  # Usamos Integer para reflejar el tipo INT en la tabla MySQL

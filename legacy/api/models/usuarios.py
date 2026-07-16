from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Definir la clase base para SQLAlchemy
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "tbusuario"
    
    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombres = Column(String(50), nullable=False)
    apellidos = Column(String(50), nullable=False)
    direccion = Column(String(150), nullable=False)
    telefono = Column(String(15), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    usuario = Column(String(50), unique=True, nullable=False)
    contra = Column(String(500), nullable=False)
    img_usuario = Column(String(100), nullable=True)
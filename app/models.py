from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

# -------------------------
# MODELO: ROL
# -------------------------
class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    usuarios = relationship("Usuario", back_populates="rol")

# -------------------------
# MODELO: USUARIO
# -------------------------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    habilitado = Column(Boolean, default=True)
    id_rol = Column(Integer, ForeignKey("roles.id"))

    rol = relationship("Rol", back_populates="usuarios")
    inscripciones = relationship("Inscripcion", back_populates="usuario")

# -------------------------
# MODELO: CURSO
# -------------------------
class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    duracion = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)  # Cambiado de "disponible" a "activo"

    inscripciones = relationship("Inscripcion", back_populates="curso")

# -------------------------
# MODELO: INSCRIPCION
# -------------------------
class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id"))
    id_curso = Column(Integer, ForeignKey("cursos.id"))
    fecha_inscripcion = Column(DateTime, default=datetime.utcnow)
    completado = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="inscripciones")
    curso = relationship("Curso", back_populates="inscripciones")

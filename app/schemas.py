from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# -------------------------
# ROLES
# -------------------------
class RolOut(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True

class RolUpdate(BaseModel):
    id_rol: int

# -------------------------
# CURSOS
# -------------------------
class CursoBase(BaseModel):
    nombre: str
    descripcion: str
    duracion: str
    activo: Optional[bool] = True

class CursoOut(CursoBase):
    id: int

    class Config:
        from_attributes = True

class CursoConParticipantes(CursoOut):
    participantes: List["UsuarioOut"] = []

    class Config:
        from_attributes = True

# -------------------------
# USUARIOS
# -------------------------
class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str
    tipo: Optional[str] = "administrador"  # Valor por defecto
    id_rol: Optional[int] = 2              # 2 = administrador

class UsuarioAdminCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    tipo: Optional[str] = None
    habilitado: Optional[bool] = None
    id_rol: Optional[int] = None

class UsuarioOut(UsuarioBase):
    id: int
    tipo: str
    id_rol: Optional[int]
    habilitado: bool
    fecha_creacion: datetime
    fecha_modificacion: datetime
    rol: Optional[RolOut]

    class Config:
        from_attributes = True

class UsuarioConCursos(UsuarioOut):
    cursos: List[CursoOut] = []

    class Config:
        from_attributes = True

# -------------------------
# INSCRIPCIONES
# -------------------------
class InscripcionBase(BaseModel):
    id_usuario: int
    id_curso: int

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionOut(InscripcionBase):
    id: int
    fecha_inscripcion: datetime
    completado: bool

    class Config:
        from_attributes = True

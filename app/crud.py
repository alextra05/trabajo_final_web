# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------
# CURSOS
# -------------------------

def get_cursos(db: Session):
    return db.query(models.Curso).all()

def create_curso(db: Session, curso: schemas.CursoBase):
    duracion = curso.duracion
    if not duracion.endswith(" semanas"):
        duracion = f"{duracion} semanas"
    nuevo = models.Curso(
        nombre=curso.nombre,
        descripcion=curso.descripcion,
        duracion=duracion,
        activo=curso.activo
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def update_curso(db: Session, curso_id: int, datos: dict):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        return None

    if "duracion" in datos:
        duracion = datos["duracion"]
        if not duracion.endswith(" semanas"):
            datos["duracion"] = f"{duracion} semanas"

    for key, value in datos.items():
        setattr(curso, key, value)

    db.commit()
    db.refresh(curso)
    return curso

def delete_curso(db: Session, curso_id: int):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        return None
    db.delete(curso)
    db.commit()
    return curso

# -------------------------
# USUARIOS
# -------------------------

def get_usuarios(db: Session):
    return db.query(models.Usuario).all()

def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    hashed_password = pwd_context.hash(usuario.password)
    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=usuario.email,
        password=hashed_password,
        tipo=usuario.tipo,
        habilitado=True,
        id_rol=usuario.id_rol or 3
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def create_administrador(db: Session, admin: schemas.UsuarioAdminCreate):
    hashed_password = pwd_context.hash(admin.password)
    db_admin = models.Usuario(
        nombre=admin.nombre,
        apellidos=admin.apellidos,
        email=admin.email,
        password=hashed_password,
        tipo="administrador",
        habilitado=True,
        id_rol=2  # 2 = administrador
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_usuario(db: Session, usuario_id: int, datos: dict):
    db_usuario = get_usuario(db, usuario_id)
    if not db_usuario:
        return None

    for campo, valor in datos.items():
        if campo == "password" and valor:
            setattr(db_usuario, campo, get_password_hash(valor))
        elif valor is not None:
            setattr(db_usuario, campo, valor)

    db_usuario.fecha_modificacion = datetime.utcnow()
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# -------------------------
# AUTENTICACIÓN
# -------------------------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    user = get_usuario_by_email(db, email)
    if not user or not verify_password(password, user.password):
        return None
    return user

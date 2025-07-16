from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from .. import schemas, crud, models
from ..database import SessionLocal
from ..deps import get_current_user


# Cargar variables de entorno para JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Registro de nuevo usuario
@router.post("/", response_model=schemas.UsuarioOut)
def registrar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, usuario.email)
    if db_usuario:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    return crud.create_usuario(db, usuario)

# Registro de nuevo administrador (ruta exclusiva)
@router.post("/admin", response_model=schemas.UsuarioOut)
def registrar_administrador(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, usuario.email)
    if db_usuario:
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )
    usuario.id_rol = 2  # Forzar rol de administrador
    return crud.create_usuario(db, usuario)

@router.get("/", response_model=List[schemas.UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    if current_user.id_rol != 1:
        raise HTTPException(status_code=403, detail="Acceso restringido a superadministradores")
    return crud.get_usuarios(db)

@router.get("/solo-usuarios", response_model=List[schemas.UsuarioOut])
def listar_usuarios_normales(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return db.query(models.Usuario).filter(models.Usuario.id_rol == 3).all()

@router.get("/me", response_model=schemas.UsuarioOut)
def leer_mi_perfil(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    usuario_con_rol = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol)
    ).filter(models.Usuario.id == current_user.id).first()
    if not usuario_con_rol:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario_con_rol

@router.put("/me", response_model=schemas.UsuarioOut)
def actualizar_mi_perfil(
    datos_actualizacion: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    usuario_db = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos_dict = datos_actualizacion.dict(exclude_unset=True)

    if "email" in datos_dict and datos_dict["email"] != usuario_db.email:
        usuario_existente = crud.get_usuario_by_email(db, datos_dict["email"])
        if usuario_existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario")

    campos_actualizables = ["nombre", "apellidos", "email", "password", "tipo", "habilitado", "id_rol"]
    for campo in campos_actualizables:
        if campo in datos_dict and datos_dict[campo] is not None:
            if campo == "password":
                setattr(usuario_db, campo, crud.get_password_hash(datos_dict[campo]))
            else:
                setattr(usuario_db, campo, datos_dict[campo])

    usuario_db.fecha_modificacion = datetime.utcnow()
    db.commit()
    db.refresh(usuario_db)

    usuario_actualizado = db.query(models.Usuario).options(
        joinedload(models.Usuario.rol)
    ).filter(models.Usuario.id == usuario_db.id).first()

    return usuario_actualizado

@router.put("/{usuario_id}/rol", response_model=schemas.UsuarioOut)
def actualizar_rol_usuario(
    usuario_id: int,
    datos: schemas.RolUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    if current_user.id_rol != 1:
        raise HTTPException(status_code=403, detail="Solo superadministradores pueden cambiar roles")

    usuario_db = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_db.id_rol = datos.id_rol
    usuario_db.fecha_modificacion = datetime.utcnow()

    db.commit()
    db.refresh(usuario_db)

    return usuario_db

@router.put("/{usuario_id}", response_model=schemas.UsuarioOut)
def actualizar_usuario_por_id(
    usuario_id: int,
    datos_actualizacion: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    if current_user.id_rol != 1:
        raise HTTPException(status_code=403, detail="Acceso restringido a superadministradores")

    usuario_db = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    datos_dict = datos_actualizacion.dict(exclude_unset=True)

    campos_actualizables = ["nombre", "apellidos", "email", "password", "id_rol", "habilitado"]
    for campo in datos_dict:
        if campo in campos_actualizables:
            if campo == "password":
                setattr(usuario_db, campo, crud.get_password_hash(datos_dict[campo]))
            else:
                setattr(usuario_db, campo, datos_dict[campo])

    usuario_db.fecha_modificacion = datetime.utcnow()
    db.commit()
    db.refresh(usuario_db)
    return usuario_db

@router.post("/inscribirse/{curso_id}", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
def inscribir_a_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    if not curso.activo:
        raise HTTPException(status_code=400, detail="Este curso no está disponible actualmente")

    inscripcion_existente = db.query(models.Inscripcion).filter(
        models.Inscripcion.id_usuario == current_user.id,
        models.Inscripcion.id_curso == curso_id
    ).first()

    if inscripcion_existente:
        raise HTTPException(status_code=400, detail="Ya estás inscrito en este curso")

    nueva_inscripcion = models.Inscripcion(
        id_usuario=current_user.id,
        id_curso=curso_id,
        fecha_inscripcion=datetime.utcnow(),
        completado=False
    )

    db.add(nueva_inscripcion)
    db.commit()
    db.refresh(nueva_inscripcion)

    return {
        "message": "Inscripción exitosa",
        "inscripcion_id": nueva_inscripcion.id,
        "curso": {
            "id": curso.id,
            "nombre": curso.nombre
        }
    }

@router.get("/mis-cursos", response_model=List[schemas.CursoOut])
def mis_cursos(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    inscripciones = db.query(models.Inscripcion).filter(
        models.Inscripcion.id_usuario == current_user.id
    ).all()

    cursos = [db.query(models.Curso).filter(models.Curso.id == ins.id_curso).first() for ins in inscripciones if ins]
    return [curso for curso in cursos if curso]

@router.get("/mis-inscripciones", response_model=List[schemas.InscripcionOut])
def mis_inscripciones(
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    return db.query(models.Inscripcion).filter(
        models.Inscripcion.id_usuario == current_user.id
    ).all()

@router.put("/cursos/{curso_id}/completar", response_model=Dict[str, Any])
def marcar_curso_completado(
    curso_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    inscripcion = db.query(models.Inscripcion).filter(
        models.Inscripcion.id_usuario == current_user.id,
        models.Inscripcion.id_curso == curso_id
    ).first()

    if not inscripcion:
        raise HTTPException(status_code=404, detail="No estás inscrito en este curso")

    inscripcion.completado = True
    db.commit()
    db.refresh(inscripcion)

    return {"message": "Curso marcado como completado", "curso_id": curso_id}

@router.delete("/cursos/{curso_id}/inscripcion", response_model=Dict[str, Any])
def cancelar_inscripcion(
    curso_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioOut = Depends(get_current_user)
):
    inscripcion = db.query(models.Inscripcion).filter(
        models.Inscripcion.id_usuario == current_user.id,
        models.Inscripcion.id_curso == curso_id
    ).first()

    if not inscripcion:
        raise HTTPException(status_code=404, detail="No estás inscrito en este curso")

    db.delete(inscripcion)
    db.commit()

    return {"message": "Inscripción cancelada correctamente", "curso_id": curso_id}

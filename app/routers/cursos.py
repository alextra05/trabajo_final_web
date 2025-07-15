# app/routers/cursos.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud
from app.database import SessionLocal
from app.deps import get_current_user

router = APIRouter(
    prefix="/cursos",
    tags=["Cursos"]
)

# Dependencia para obtener sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Obtener todos los cursos
@router.get("/", response_model=List[schemas.CursoOut])
def listar_cursos(db: Session = Depends(get_db)):
    return crud.get_cursos(db)

# Obtener curso por ID
@router.get("/{curso_id}", response_model=schemas.CursoOut)
def obtener_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

# Crear nuevo curso (solo admin o super)
@router.post("/", response_model=schemas.CursoOut)
def crear_curso(
    curso: schemas.CursoBase,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="Solo administradores o super pueden crear cursos")
    return crud.create_curso(db, curso)

# Editar curso existente (solo admin o super)
@router.put("/{curso_id}", response_model=schemas.CursoOut)
def editar_curso(
    curso_id: int,
    datos: schemas.CursoBase,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado para editar cursos")

    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    curso.nombre = datos.nombre
    curso.descripcion = datos.descripcion
    curso.duracion = datos.duracion
    curso.activo = datos.activo

    db.commit()
    db.refresh(curso)
    return curso

# Eliminar un curso
@router.delete("/{curso_id}")
def eliminar_curso(
    curso_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    db.delete(curso)
    db.commit()
    return {"message": "Curso eliminado correctamente"}

# Cambiar estado activo/inactivo
@router.put("/{curso_id}/estado")
def cambiar_estado_curso(
    curso_id: int,
    estado: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user.id_rol not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")

    curso.activo = estado.get("activo", curso.activo)
    db.commit()
    db.refresh(curso)
    return {"message": f"Curso {'activado' if curso.activo else 'desactivado'} correctamente"}

# Obtener participantes
@router.get("/{curso_id}/participantes", response_model=List[schemas.UsuarioOut])
def obtener_participantes(
    curso_id: int, 
    db: Session = Depends(get_db)
):
    curso = db.query(models.Curso).filter(models.Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    usuarios = db.query(models.Usuario).join(
        models.Inscripcion, 
        models.Usuario.id == models.Inscripcion.id_usuario
    ).filter(
        models.Inscripcion.id_curso == curso_id
    ).all()
    
    return usuarios

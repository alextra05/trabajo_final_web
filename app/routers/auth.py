

# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .. import crud, schemas
from ..deps import get_db
import os
from dotenv import load_dotenv



# Cargar configuración del entorno
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ============================
# FUNCIONES AUXILIARES
# ============================

# Crear token JWT
def crear_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obtener el usuario autenticado a partir del token Bearer
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_usuario_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Decorador para restricción de roles
def role_required(allowed_roles: list):
    def dependency(current_user: schemas.UsuarioOut = Depends(get_current_user)):
        if current_user.id_rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso"
            )
        return current_user
    return dependency

# ============================
# RUTAS DE AUTENTICACIÓN
# ============================

# Login API - devuelve token
@router.post("/login")
def login_api(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Credenciales incorrectas")

    access_token = crear_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id_rol": user.id_rol,  # Añadido id_rol directamente a la respuesta principal
        "usuario": {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "tipo": user.tipo,
            "id_rol": user.id_rol
        }
    }

# Registro de usuario API
@router.post("/register")
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_by_email(db, usuario.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario.id_rol = 3  # Rol por defecto: usuario normal
    nuevo_usuario = crud.create_usuario(db, usuario)
    access_token = crear_token(data={"sub": nuevo_usuario.email})

    return {
        "message": "Usuario registrado correctamente",
        "access_token": access_token,
        "token_type": "bearer",
        "id_rol": nuevo_usuario.id_rol,  # Añadido id_rol directamente a la respuesta principal
        "usuario": {
            "id": nuevo_usuario.id,
            "email": nuevo_usuario.email,
            "nombre": nuevo_usuario.nombre,
            "tipo": nuevo_usuario.tipo,
            "id_rol": nuevo_usuario.id_rol
        }
    }

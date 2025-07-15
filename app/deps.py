# app/deps.py
from fastapi import Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.database import SessionLocal
from app import crud, schemas
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuración del token
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# OAuth2 token bearer (con auto_error=False para permitir otras fuentes)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para extraer el token de diferentes fuentes
async def extract_token_from_request(request: Request) -> Optional[str]:
    # Intentar obtener de cookies
    token = request.cookies.get("access_token")
    
    # Si no está en cookies, intentar obtenerlo del header Authorization manualmente
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
    
    # Si no está en headers, intentar obtenerlo de localStorage a través del formulario
    if not token and request.method == "POST":
        try:
            form_data = await request.form()
            token = form_data.get("access_token")
        except Exception as e:
            print(f"Error al obtener datos del formulario: {str(e)}")
    
    # Intentar obtener de la query (URL)
    if not token:
        token = request.query_params.get("token")
    
    return token

# Función para obtener el usuario actual para rutas de API (usando Depends)
async def get_current_user_api(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> schemas.UsuarioOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        # Decodificar y verificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_usuario_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user

# Función para obtener el usuario actual para rutas de páginas (sin usar Depends para el token)
async def get_current_user(request: Request) -> schemas.UsuarioOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Obtener la sesión de la base de datos
    db = SessionLocal()
    try:
        # Extraer el token de la solicitud
        token = await extract_token_from_request(request)
        
        # Si no se encontró token en ninguna fuente, lanzar excepción
        if not token:
            print("No se encontró token en ninguna fuente")
            raise credentials_exception
        
        try:
            # Decodificar y verificar el token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                print("No se encontró 'sub' en el payload del token")
                raise credentials_exception
        except JWTError as e:
            print(f"Error al decodificar token: {str(e)}")
            raise credentials_exception
        
        # Obtener el usuario de la base de datos
        user = crud.get_usuario_by_email(db, email)
        if user is None:
            print(f"No se encontró usuario con email: {email}")
            raise credentials_exception
        
        print(f"Usuario autenticado correctamente: {user.email}")
        return user
    finally:
        db.close()

# Función auxiliar para verificar roles
def check_user_role(user: schemas.UsuarioOut, allowed_roles: list):
    if user.id_rol not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a este recurso"
        )
    return user

# Función para requerir un rol específico
async def require_role(request: Request, allowed_roles: list):
    user = await get_current_user(request)
    return check_user_role(user, allowed_roles)
# app/main.py
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.routers import auth, usuarios, cursos  # 👈 ¡sin superadmin!
from app.deps import get_current_user



app = FastAPI(title="Academia de Programación")

# =========================
# MIDDLEWARE CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MIDDLEWARE PARA MANEJAR ERRORES DE AUTENTICACIÓN
# =========================
@app.middleware("http")
async def handle_auth_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        if e.status_code == 401:
            # Redireccionar a login con la URL original como parámetro next
            return RedirectResponse(url=f"/login?next={request.url.path}", status_code=302)
        raise e

# =========================
# ARCHIVOS ESTÁTICOS Y TEMPLATES
# =========================
app.mount("/static", StaticFiles(directory="app/frontend_web"), name="static")
templates = Jinja2Templates(directory="app/frontend_web")

# =========================
# PÁGINAS HTML
# =========================

# ✅ Home no necesita autenticación obligatoria
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inicio", response_class=HTMLResponse)
def inicio_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    next_page = request.query_params.get("next", "/")
    return templates.TemplateResponse("login.html", {"request": request, "next": next_page})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ✅ Estas páginas sí necesitan token Bearer, pero controladas
@app.get("/panel", response_class=HTMLResponse)
async def panel(request: Request):
    try:
        current_user = await get_current_user(request)
        print(f"Usuario accediendo a /panel: {current_user.email}, rol: {current_user.id_rol}")
        
        if current_user.id_rol == 1:
            return RedirectResponse(url="/super")
        elif current_user.id_rol == 2:
            return RedirectResponse(url="/admin")
        elif current_user.id_rol == 3:
            return RedirectResponse(url="/")
        else:
            print(f"Rol no reconocido: {current_user.id_rol}")
            return RedirectResponse(url="/login")
    except HTTPException as e:
        print(f"Error en /panel: {str(e)}")
        return RedirectResponse(url="/login?next=/panel")
    except Exception as e:
        print(f"Error inesperado en /panel: {str(e)}")
        return RedirectResponse(url="/login?next=/panel")

@app.get("/super", response_class=HTMLResponse)
async def super_page(request: Request):
    try:
        current_user = await get_current_user(request)
        print(f"Usuario accediendo a /super: {current_user.email}, rol: {current_user.id_rol}")
        
        # Verificar que el usuario sea de tipo supervisor (rol 1)
        if current_user.id_rol != 1:
            print(f"Acceso denegado a /super: rol incorrecto ({current_user.id_rol})")
            return RedirectResponse(url="/panel")
        
        return templates.TemplateResponse("super.html", {"request": request, "user": current_user})
    except HTTPException as e:
        print(f"Error en /super: {str(e)}")
        return RedirectResponse(url="/login?next=/super")
    except Exception as e:
        print(f"Error inesperado en /super: {str(e)}")
        return RedirectResponse(url="/login?next=/super")

@app.get("/super.html", response_class=HTMLResponse)
def super_html_page(request: Request):
    # Redirigir a la versión sin .html
    return RedirectResponse(url="/super")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        current_user = await get_current_user(request)
        print(f"Usuario accediendo a /admin: {current_user.email}, rol: {current_user.id_rol}")
        
        # Verificar que el usuario sea de tipo administrador (rol 2) o supervisor (rol 1)
        if current_user.id_rol not in [1, 2]:
            print(f"Acceso denegado a /admin: rol incorrecto ({current_user.id_rol})")
            return RedirectResponse(url="/", status_code=303)  # Usar 303 See Other para forzar GET
        
        # Solo renderizar la plantilla si el usuario tiene los permisos correctos
        return templates.TemplateResponse("admin.html", {"request": request, "user": current_user})
    except HTTPException as e:
        print(f"Error en /admin: {str(e)}")
        return RedirectResponse(url="/login?next=/admin", status_code=303)
    except Exception as e:
        print(f"Error inesperado en /admin: {str(e)}")
        return RedirectResponse(url="/login?next=/admin", status_code=303)

@app.get("/admin.html", response_class=HTMLResponse)
def admin_html_page(request: Request):
    # Redirigir a la versión sin .html
    return RedirectResponse(url="/admin")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("dashboard.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/dashboard")

@app.get("/dashboard.html", response_class=HTMLResponse)
def dashboard_html_page(request: Request):
    # Redirigir a la versión sin .html
    return RedirectResponse(url="/dashboard")

@app.get("/curso/{curso_id}", response_class=HTMLResponse)
def curso_page(curso_id: int, request: Request):
    return templates.TemplateResponse("curso.html", {"request": request, "curso_id": curso_id})

@app.get("/perfil", response_class=HTMLResponse)
async def perfil_page(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("perfil.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/perfil")

@app.post("/perfil", response_class=HTMLResponse)
async def perfil_post(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("perfil.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/perfil")

@app.get("/mis-cursos", response_class=HTMLResponse)
async def mis_cursos_page(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("mis-cursos.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/mis-cursos")

@app.post("/mis-cursos", response_class=HTMLResponse)
async def mis_cursos_post(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("mis-cursos.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/mis-cursos")

@app.get("/mis-cursos.html", response_class=HTMLResponse)
def mis_cursos_html_page():
    return RedirectResponse(url="/mis-cursos")

@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion_page(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("configuracion.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/configuracion")

@app.post("/configuracion", response_class=HTMLResponse)
async def configuracion_post(request: Request):
    try:
        current_user = await get_current_user(request)
        return templates.TemplateResponse("configuracion.html", {"request": request, "user": current_user})
    except HTTPException:
        return RedirectResponse(url="/login?next=/configuracion")

# Ruta para verificar el token y redirigir según el rol
@app.get("/auth-check", response_class=HTMLResponse)
async def auth_check(request: Request):
    try:
        current_user = await get_current_user(request)
        # Imprimir para depuración
        print(f"Usuario autenticado en /auth-check: {current_user.email}, rol: {current_user.id_rol}")
        
        # Redirigir según el rol del usuario
        if current_user.id_rol == 1:
            return RedirectResponse(url="/super")
        elif current_user.id_rol == 2:
            return RedirectResponse(url="/admin")
        elif current_user.id_rol == 3:
            return RedirectResponse(url="/")
        else:
            # Si no tiene un rol válido, redirigir al login
            print(f"Rol no válido: {current_user.id_rol}")
            return RedirectResponse(url="/login")
    except HTTPException as e:
        print(f"Error en /auth-check: {str(e)}")
        return RedirectResponse(url="/login")
    except Exception as e:
        print(f"Error inesperado en /auth-check: {str(e)}")
        return RedirectResponse(url="/login")

# =========================
# API (REST)
# =========================
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(cursos.router)

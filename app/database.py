# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# -------------------------
# CARGAR VARIABLES DE ENTORNO
# -------------------------
load_dotenv()

# URL de conexión a la base de datos (desde .env)
DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------------
# CONEXIÓN A MYSQL
# -------------------------
engine = create_engine(DATABASE_URL, echo=True)

# Sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos ORM
Base = declarative_base()

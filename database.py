import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from config import DATABASE_URL

# Cargar variables de entorno
load_dotenv()


# Crear el motor de base de datos
engine = create_engine(DATABASE_URL)

# Crear sesión con SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

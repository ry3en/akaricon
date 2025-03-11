from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependences import get_db
from models import User
from schemas import UserCreate, UserLogin, Token
from security import create_access_token
from passlib.context import CryptContext

# Instancia de router
router = APIRouter(tags=["Authentication"])

# Instancia de CryptContext para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Endpoint para registrar un nuevo usuario
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(User.Username == user.Username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # Crear hash de la contraseña
    hashed_password = pwd_context.hash(user.Password)

    # Crear nuevo usuario
    new_user = User(
        Username=user.Username,
        Phone=user.Phone,
        Password=hashed_password,
    )

    # Guardar usuario en la base de datos
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User registered successfully"}


# Endpoint para login
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Verificar si el usuario existe
    user = db.query(User).filter(User.Username == user_data.Username).first()

    if not user or not pwd_context.verify(user_data.Password, user.Password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token JWT
    access_token = create_access_token(data={"sub": user.Username})

    return {
        "access_token": access_token,
        "Username": user.Username,
        "User_type": user.User_type,
        "ID_user": user.ID_user
    }
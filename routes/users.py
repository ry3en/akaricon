from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from dependences import get_db
from models import User
from passlib.context import CryptContext

from schemas import UserResponse, UserUpdate

# Instancia de router
router = APIRouter(tags=["Users"])

# Instancia de CryptContext para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Endpoint para obtener todos los usuarios
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# Endpoint para obtener un usuario específico
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.ID_user == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Endpoint para actualizar un usuario
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.ID_user == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Actualizar los campos proporcionados
    update_data = user_update.dict(exclude_unset=True)

    # Si se proporciona una nueva contraseña, hacer hash
    if "Password" in update_data and update_data["Password"]:
        update_data["Password"] = pwd_context.hash(update_data["Password"])

    # Actualizar la marca de tiempo
    update_data["UpdatedAt"] = datetime.now()

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)

    return db_user


# Endpoint para eliminar un usuario
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.ID_user == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(db_user)
    db.commit()

    return {"status": f"User with ID {user_id} deleted successfully"}
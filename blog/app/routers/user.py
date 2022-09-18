from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from typing import List

from .. import models, schemas, oauth2, user_repository
from ..database import Base

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.User, db: Session = Depends(Base.get_db)):
    """Create a new user"""
    db_user = user_repository.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists.")
    return user_repository.create_user(db=db, user=user)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(Base.get_db)):
    """Get all the users"""
    users = user_repository.get_users(db)
    return users


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(Base.get_db)):
    """Get a user by id"""
    user = user_repository.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_user(id: int, db: Session = Depends(Base.get_db)):
    """Delete a user by id"""
    user = user_repository.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_repository.delete_user(db, user)

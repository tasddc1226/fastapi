from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from typing import List

from .. import models, schemas
from ..database import Base
from ..utils.password import hash_password

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
async def create_user(user: schemas.User, db: Session = Depends(Base.get_db)):
    """Create a new user"""
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    try:
        new_user = models.User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate email")

    return new_user


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(Base.get_db)):
    """Get all the users"""
    users = db.query(models.User).all()
    return users


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user_by_id(id: int, db: Session = Depends(Base.get_db)):
    """Get a user by id"""
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{id}")
def delete_user_by_id(id: int, db: Session = Depends(Base.get_db)):
    """Delete a user by id"""
    user = db.query(models.User).filter(models.User.id == id)
    if user.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist!"
        )

    try:
        user.delete()
        db.commit()
    except Exception as e:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)

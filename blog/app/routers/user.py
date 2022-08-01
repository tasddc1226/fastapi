from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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

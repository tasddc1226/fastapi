from app import user_repository
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import schemas, models, oauth2
from ..database import Base
from ..utils.password import verify_password

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=schemas.Token)
def login(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(Base.get_db)):
    user = user_repository.get_user_by_email(db, login.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="E-mail does not exist")

    if not verify_password(login.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect password")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

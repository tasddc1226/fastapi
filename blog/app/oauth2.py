from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from .database import Base
from .core.config import settings
from . import schemas, models, user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    return user_id


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(Base.get_db)
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_from_user_id = verify_access_token(token, credentials_exception)
    user = user_repository.get_user_by_id(db, token_from_user_id)
    return user

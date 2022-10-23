from datetime import datetime
import secrets
from fastapi import Response, status, HTTPException, Depends, APIRouter, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import Session
import os
from fastapi.responses import FileResponse


from typing import Optional, List

from ..database import Base
from .. import models, schemas, oauth2

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostLike])
def get_posts(
    db: Session = Depends(Base.get_db),
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = "",
):
    """Get a list of posts from the database using the given query parameters"""
    posts = (
        db.query(models.Post, func.count(models.Like.post_id).label("likes"))
        .join(models.Like, models.Like.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.CreatePost,
    db: Session = Depends(Base.get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user),
):
    """Create a new post"""
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static/")
IMG_DIR = os.path.join(STATIC_DIR, "images/")
SERVER_IMG_DIR = os.path.join("http://localhost:8000/", "static/", "images/")


@router.post("/upload-images", status_code=status.HTTP_201_CREATED)
async def upload_image(in_files: List[UploadFile] = File(...)):
    file_urls = []
    for file in in_files:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = "".join([now, secrets.token_hex(16)])

        file_location = os.path.join(IMG_DIR, file_name)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        file_urls.append(SERVER_IMG_DIR + file_name)
    result = {"file_urls": file_urls}
    return result


@router.get("/images/{file_name}", status_code=status.HTTP_200_OK)
def get_image(file_name: str):
    return FileResponse("".join([IMG_DIR, file_name]))

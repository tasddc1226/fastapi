from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session

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
    current_user: int = Depends(oauth2.get_current_user),
):
    """Create a new post"""
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

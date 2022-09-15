from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from ..database import Base
from .. import schemas, models, oauth2

router = APIRouter(tags=["Likes"])


@router.post("/like", status_code=status.HTTP_201_CREATED)
def like(
    like: schemas.Like,
    db: Session = Depends(Base.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == like.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post does not exist",
        )

    like_query = db.query(models.Like).filter(
        models.Like.post_id == like.post_id, models.Like.user_id == current_user.id
    )

    if like.dir == 1:
        if like_query.first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="already liked on this post"
            )
        new_like = models.Like(post_id=like.post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()

        return {"message": "Successfully liked this post"}
    else:
        if not like_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Like does not exist")

        like_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "Like has been deleted"}

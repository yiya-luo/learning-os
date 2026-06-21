"""User API — get and update current user profile."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.models import User
from app.models.schemas import UpdateUserRequest, UserResponse
from app.services.reward import get_level_info

router = APIRouter(prefix="/api", tags=["User"])


def _user_to_response(user: User, level_info=None) -> UserResponse:
    if level_info is None:
        level_info = get_level_info(user.xp)
    return UserResponse(
        id=user.id,
        nickname=user.nickname,
        avatar=user.avatar,
        xp=user.xp,
        level=level_info.level,
        streak=user.streak,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/users/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return _user_to_response(user)


@router.patch("/users/me", response_model=UserResponse)
def update_me(body: UpdateUserRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.avatar is not None:
        user.avatar = body.avatar

    db.commit()
    db.refresh(user)
    return _user_to_response(user)

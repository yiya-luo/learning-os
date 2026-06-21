from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import wechat_code2session, generate_session_token, get_current_user
from app.database import get_db
from app.models.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str
    user_id: str
    nickname: str
    avatar: str | None
    is_new: bool


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    wx_data = await wechat_code2session(body.code)
    openid = wx_data["openid"]

    user = db.query(User).filter(User.openid == openid).first()
    is_new = False
    if not user:
        user = User(openid=openid)
        db.add(user)
        is_new = True

    user.session_token = generate_session_token()
    db.commit()
    db.refresh(user)

    return LoginResponse(
        token=user.session_token,
        user_id=user.id,
        nickname=user.nickname,
        avatar=user.avatar,
        is_new=is_new,
    )


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "xp": user.xp,
        "level": user.level,
        "streak": user.streak,
    }

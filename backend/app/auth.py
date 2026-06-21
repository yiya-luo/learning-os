import secrets

import httpx
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.config import WECHAT_APPID, WECHAT_SECRET
from app.database import get_db
from app.models.models import User


async def wechat_code2session(code: str) -> dict:
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WECHAT_APPID,
        "secret": WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
    if "openid" not in data:
        raise HTTPException(status_code=401, detail=data.get("errmsg", "code2session failed"))
    return data


def generate_session_token() -> str:
    return secrets.token_hex(32)


def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization[7:]
    user = db.query(User).filter(User.session_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

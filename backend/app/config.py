import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learning_os.db")

WECHAT_APPID = os.getenv("WECHAT_APPID", "wx80c67e5edc61479a")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")

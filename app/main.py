from fastapi import FastAPI

from app.database import Base, engine
from app.models import post  # noqa: F401  모델을 import해야 create_all이 posts 테이블을 안다
from app.routers import home_router, post_router

# 서버가 켜질 때 테이블이 없으면 만든다. (이미 있으면 그대로 둔다)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="공부 기록 블로그")
app.include_router(home_router.router)
app.include_router(post_router.router)

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 어느 폴더에서 서버를 실행해도 DB 파일이 항상 프로젝트 루트에 생기도록 절대경로로 만든다.
BASE_DIR = Path(__file__).resolve().parent.parent
# 다른 DB를 쓰려면 코드를 고치지 않고 환경변수 DATABASE_URL만 바꾼다. (비밀번호가 코드에 남지 않게)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.db'}")

# check_same_thread=False: FastAPI는 여러 스레드에서 요청을 처리하므로 SQLite의 기본 제한을 푼다. (SQLite 전용 옵션)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """요청 하나당 세션 하나를 열고, 응답이 끝나면 반드시 닫는다. (Depends로 주입)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 어느 폴더에서 서버를 실행해도 DB 파일이 항상 프로젝트 루트에 생기도록 절대경로로 만든다.
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'database.db'}"

# check_same_thread=False: FastAPI는 여러 스레드에서 요청을 처리하므로 SQLite의 기본 제한을 푼다.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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

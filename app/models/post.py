from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Post(Base):
    """공부 기록 글 1개 = posts 테이블의 행(row) 1개"""

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    # onupdate: 행이 수정될 때마다 SQLAlchemy가 자동으로 현재 시각을 넣어준다.
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

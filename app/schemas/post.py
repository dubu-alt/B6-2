from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PostRead(BaseModel):
    """화면(템플릿)에 넘겨줄 글 데이터. ORM 모델을 직접 넘기지 않기 위한 DTO."""

    # from_attributes=True: post.title 처럼 '속성'으로 된 ORM 객체에서 값을 읽어올 수 있게 한다.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    category: str
    created_at: datetime
    updated_at: datetime

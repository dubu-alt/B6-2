from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.post import Post


def find_all(db: Session, keyword: str = "", category: str = "") -> list[Post]:
    stmt = select(Post).order_by(Post.created_at.desc())
    if keyword:
        # contains() → SQL의 LIKE '%keyword%'. autoescape=True: 검색어 속 %, _ 를 글자 그대로 취급
        stmt = stmt.where(
            or_(
                Post.title.contains(keyword, autoescape=True),
                Post.content.contains(keyword, autoescape=True),
            )
        )
    if category:
        stmt = stmt.where(Post.category == category)
    return list(db.scalars(stmt))


def find_by_id(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def find_categories(db: Session) -> list[str]:
    return list(db.scalars(select(Post.category).distinct().order_by(Post.category)))


def save(db: Session, post: Post) -> Post:
    """새 글이면 INSERT, 이미 있는 글이면 바뀐 부분만 UPDATE 된다."""
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def delete(db: Session, post: Post) -> None:
    db.delete(post)
    db.commit()

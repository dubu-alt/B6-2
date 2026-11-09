from sqlalchemy.orm import Session

from app.models.post import Post
from app.repositories import post_repository
from app.schemas.post import PostRead

DEFAULT_CATEGORY = "기타"


class PostNotFoundError(Exception):
    pass


class PostValidationError(Exception):
    def __init__(self, errors: dict[str, str]):
        super().__init__("입력값이 올바르지 않습니다.")
        self.errors = errors


def _clean(title: str, content: str, category: str) -> dict[str, str]:
    """입력값 앞뒤 공백을 지우고 규칙을 검사한다. 틀리면 PostValidationError."""
    title, content, category = title.strip(), content.strip(), category.strip()
    errors = {}
    if not title:
        errors["title"] = "제목을 입력해 주세요."
    elif len(title) > 100:
        errors["title"] = "제목은 100자 이내로 입력해 주세요."
    if not content:
        errors["content"] = "내용을 입력해 주세요."
    if len(category) > 30:
        errors["category"] = "카테고리는 30자 이내로 입력해 주세요."
    if errors:
        raise PostValidationError(errors)
    return {"title": title, "content": content, "category": category or DEFAULT_CATEGORY}


def _get_or_raise(db: Session, post_id: int) -> Post:
    post = post_repository.find_by_id(db, post_id)
    if post is None:
        raise PostNotFoundError()
    return post


def list_posts(db: Session, keyword: str = "", category: str = "") -> list[PostRead]:
    posts = post_repository.find_all(db, keyword.strip(), category.strip())
    return [PostRead.model_validate(p) for p in posts]


def list_categories(db: Session) -> list[str]:
    return post_repository.find_categories(db)


def get_post(db: Session, post_id: int) -> PostRead:
    return PostRead.model_validate(_get_or_raise(db, post_id))


def create_post(db: Session, title: str, content: str, category: str) -> PostRead:
    data = _clean(title, content, category)
    return PostRead.model_validate(post_repository.save(db, Post(**data)))


def update_post(db: Session, post_id: int, title: str, content: str, category: str) -> PostRead:
    post = _get_or_raise(db, post_id)
    data = _clean(title, content, category)
    post.title, post.content, post.category = data["title"], data["content"], data["category"]
    return PostRead.model_validate(post_repository.save(db, post))


def delete_post(db: Session, post_id: int) -> None:
    post_repository.delete(db, _get_or_raise(db, post_id))

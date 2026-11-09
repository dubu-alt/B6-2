from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import post_service
from app.services.post_service import PostNotFoundError, PostValidationError
from app.templating import templates

router = APIRouter(prefix="/posts")


def _not_found(request: Request):
    return templates.TemplateResponse(request, "not_found.html", status_code=404)


def _form_page(request: Request, db: Session, action: str, form: dict, errors=None, status_code=200):
    return templates.TemplateResponse(
        request,
        "form.html",
        {
            "action": action,
            "form": form,
            "errors": errors or {},
            "categories": post_service.list_categories(db),
        },
        status_code=status_code,
    )


@router.get("")
def list_posts(request: Request, q: str = "", category: str = "", db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "list.html",
        {
            "posts": post_service.list_posts(db, q, category),
            "categories": post_service.list_categories(db),
            "q": q,
            "category": category,
        },
    )


# /posts/new 는 /posts/{post_id} 보다 먼저 등록해야 한다. (위에서부터 순서대로 주소를 맞춰 보기 때문)
@router.get("/new")
def new_form(request: Request, db: Session = Depends(get_db)):
    return _form_page(request, db, "/posts", {})


# Form("") : 빈 칸이 와도 FastAPI가 422 에러를 내지 않고, 검증은 서비스가 맡는다.
@router.post("")
def create(
    request: Request,
    title: str = Form(""),
    content: str = Form(""),
    category: str = Form(""),
    db: Session = Depends(get_db),
):
    try:
        post = post_service.create_post(db, title, content, category)
    except PostValidationError as e:
        form = {"title": title, "content": content, "category": category}
        return _form_page(request, db, "/posts", form, e.errors, status_code=400)
    return RedirectResponse(f"/posts/{post.id}", status_code=303)


@router.get("/{post_id}")
def detail(request: Request, post_id: int, db: Session = Depends(get_db)):
    try:
        post = post_service.get_post(db, post_id)
    except PostNotFoundError:
        return _not_found(request)
    return templates.TemplateResponse(request, "detail.html", {"post": post})


@router.get("/{post_id}/edit")
def edit_form(request: Request, post_id: int, db: Session = Depends(get_db)):
    try:
        post = post_service.get_post(db, post_id)
    except PostNotFoundError:
        return _not_found(request)
    return _form_page(request, db, f"/posts/{post_id}/edit", post.model_dump())


@router.post("/{post_id}/edit")
def update(
    request: Request,
    post_id: int,
    title: str = Form(""),
    content: str = Form(""),
    category: str = Form(""),
    db: Session = Depends(get_db),
):
    try:
        post_service.update_post(db, post_id, title, content, category)
    except PostNotFoundError:
        return _not_found(request)
    except PostValidationError as e:
        form = {"id": post_id, "title": title, "content": content, "category": category}
        return _form_page(request, db, f"/posts/{post_id}/edit", form, e.errors, status_code=400)
    return RedirectResponse(f"/posts/{post_id}", status_code=303)


@router.post("/{post_id}/delete")
def delete(request: Request, post_id: int, db: Session = Depends(get_db)):
    try:
        post_service.delete_post(db, post_id)
    except PostNotFoundError:
        return _not_found(request)
    return RedirectResponse("/posts", status_code=303)

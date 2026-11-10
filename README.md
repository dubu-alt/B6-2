# 📚 공부 기록 블로그

매일 공부한 내용을 글로 남기는 블로그형 웹 서비스입니다.
FastAPI와 SQLAlchemy로 만들었고, 글을 **등록 · 목록 · 상세 · 수정 · 삭제(CRUD)** 할 수 있습니다.

## 주요 기능

- 글 등록, 목록, 상세, 수정, 삭제
- 등록/수정/삭제 후 **PRG 패턴**(POST → 303 Redirect → GET)으로 새로고침 시 중복 요청 방지
- 제목/내용 **검색** (`/posts?q=검색어`)
- **카테고리별 보기** (`/posts?category=Python`)
- 필수값 **검증**: 제목·내용이 비어 있으면 저장하지 않고 안내 문구 표시
- 삭제 전 **확인 창**
- 존재하지 않는 글은 "해당 글을 찾을 수 없습니다" 안내 화면(404)

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 언어 | Python 3.10 이상 |
| 웹 프레임워크 | FastAPI, Uvicorn |
| DB / ORM | SQLite, SQLAlchemy 2.x |
| 화면 | Jinja2 템플릿 (SSR) |
| 폼 처리 | python-multipart |

## 실행 방법

### 1. 저장소 받기

```bash
git clone https://github.com/<your-github-id>/B6-2.git
cd B6-2
```

### 2. 가상환경 만들고 켜기

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 서버 실행

```bash
uvicorn app.main:app --reload
```

아래 로그가 보이면 정상 실행된 것입니다.

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

브라우저에서 <http://localhost:8000> 에 접속합니다.
서버가 처음 켜질 때 프로젝트 폴더에 `database.db` 파일이 자동으로 만들어집니다.

## 화면과 URL

| 메서드 | URL | 화면 / 동작 |
|---|---|---|
| GET | `/` | 홈 |
| GET | `/posts` | 글 목록 (검색 `?q=`, 카테고리 `?category=`) |
| GET | `/posts/new` | 새 글 작성 폼 |
| POST | `/posts` | 글 등록 → `/posts/{id}` 로 303 리다이렉트 |
| GET | `/posts/{id}` | 글 상세 |
| GET | `/posts/{id}/edit` | 글 수정 폼 |
| POST | `/posts/{id}/edit` | 글 수정 → `/posts/{id}` 로 303 리다이렉트 |
| POST | `/posts/{id}/delete` | 글 삭제 → `/posts` 로 303 리다이렉트 |

## 프로젝트 구조

```
B6-2/
├── app/
│   ├── main.py                 # 앱 시작점: 테이블 생성, 라우터 등록
│   ├── database.py             # DB 연결, 세션 공급(get_db → Depends)
│   ├── templating.py           # Jinja2 템플릿 설정
│   ├── models/post.py          # SQLAlchemy ORM 모델 (posts 테이블)
│   ├── schemas/post.py         # Pydantic 스키마 (화면에 넘기는 DTO)
│   ├── repositories/post_repository.py  # 데이터 접근 (DB 읽기/쓰기)
│   ├── services/post_service.py         # 비즈니스 로직 (검증, 없는 글 처리)
│   ├── routers/
│   │   ├── home_router.py      # GET /
│   │   └── post_router.py      # /posts 요청/응답, 리다이렉트
│   └── templates/              # base, home, list, detail, form, not_found
├── docs/
│   ├── architecture.svg        # 전체 구조 그림
│   └── screenshots/            # 주요 화면 스크린샷
├── requirements.txt
└── README.md
```

## 전체 구조

![서버 안과 바깥의 요청 흐름](docs/architecture.svg)

- **서버 바깥**: 브라우저와 서버는 HTTP 요청·응답만 주고받습니다.
- **서버 안**: 요청은 `routers → services → repositories → database.db` 순서로 내려갔다가 다시 올라옵니다. (청록색: 요청이 지나가는 층)
- 각 층은 옆의 도구를 가져다 씁니다. (회색) 라우터는 `templates/`로 HTML을 만들고, 서비스는 `schemas/`(DTO)로 데이터를 포장하며, 저장소는 `models/`(테이블 설계도)로 DB를 다룹니다.
- 브라우저와 맞닿은 층은 라우터뿐이므로 `Request`, `Form`, `RedirectResponse`, `TemplateResponse`는 `routers/`에만 있습니다.

## 요청 흐름 (글 등록 예시)

```
브라우저  POST /posts  (폼: title, content, category)
  → routers   post_router.create        Form()으로 입력값 받기
  → services  post_service.create_post  공백 제거, 필수값 검증, 카테고리 기본값
  → repositories post_repository.save   session.add → commit → refresh
  → SQLite (database.db)
  ← 303 Redirect: /posts/{id}
브라우저  GET /posts/{id}
  → router → service → repository → 템플릿(detail.html) 렌더링
```

| 레이어 | 하는 일 | 모르는 것 |
|---|---|---|
| Router | URL, 폼 입력, 화면 선택, 리다이렉트 | DB, 검증 규칙의 세부 내용 |
| Service | 앱의 규칙 (검증, 없는 글 처리) | SQL, HTML |
| Repository | SQLAlchemy로 DB 읽기/쓰기 | 검증 규칙, 화면 |

## 데이터 모델 (`posts` 테이블)

| 필드 | 타입 | 설명 |
|---|---|---|
| id | INTEGER | 글 번호 (자동 증가) |
| title | VARCHAR(100) | 제목 (필수) |
| content | TEXT | 내용 (필수) |
| category | VARCHAR(30) | 카테고리 (비우면 "기타") |
| created_at | DATETIME | 작성일시 (자동) |
| updated_at | DATETIME | 수정일시 (수정 시 자동 갱신) |

## 저장된 데이터 직접 확인하기

[DB Browser for SQLite](https://sqlitebrowser.org/)로 `database.db`를 열거나, **프로젝트 루트(`B6-2/`)에서** 아래 명령으로 확인할 수 있습니다.
서버를 한 번 이상 실행해서 `database.db`가 만들어진 뒤에 실행합니다.

```bash
python3 -c "import sqlite3; [print(r) for r in sqlite3.connect('file:database.db?mode=ro', uri=True).execute('SELECT id, title, category, created_at FROM posts')]"
```

> `mode=ro`(읽기 전용)를 붙인 이유: 다른 폴더에서 실행하면 `sqlite3.connect()`가 그 폴더에 **빈 DB 파일을 새로 만들어** `no such table: posts` 에러가 납니다. 읽기 전용으로 열면 새 파일을 만들지 않고 `unable to open database file` 에러로 바로 알려 줍니다.

## 설계 설명과 확장 가이드

### 1. 레이어를 나누지 않으면 생기는 문제

아래는 레이어를 나누지 않고 **라우터 한 곳에 검증 + DB 접근 + 화면 처리를 섞은** 예시입니다. (이 프로젝트에서는 이렇게 하지 않았습니다.)

```python
# ❌ 나쁜 예: 라우터가 모든 일을 한다
@router.post("/posts")
def create(title: str = Form(""), content: str = Form(""), db: Session = Depends(get_db)):
    if not title.strip():                                  # 검증 규칙
        return templates.TemplateResponse(...)
    post = Post(title=title.strip(), content=content)      # DB 객체 생성
    db.add(post); db.commit()                              # DB 접근
    return RedirectResponse(f"/posts/{post.id}", status_code=303)
```

| 문제 | 구체적으로 무슨 일이 생기나 |
|---|---|
| **규칙이 여러 곳에 복사됨** | 등록·수정 라우터에 같은 검증 코드가 두 번 들어갑니다. "제목 100자 제한"을 추가할 때 한 곳만 고치면 등록과 수정의 규칙이 서로 달라지는 버그가 생깁니다. |
| **DB 변경이 전체로 번짐** | `db.add`, `select()` 같은 코드가 라우터마다 흩어져 있어서, DB나 조회 방식을 바꾸면 모든 라우터를 고쳐야 합니다. |
| **화면 방식 변경이 어려움** | 검증과 저장이 HTML 응답 코드와 묶여 있어서, 같은 기능을 JSON API로 제공하려면 로직을 통째로 다시 써야 합니다. |
| **테스트가 어려움** | "빈 제목이면 저장 안 됨"을 확인하려면 매번 서버를 띄우고 폼을 보내야 합니다. 서비스로 분리하면 함수 하나만 호출해서 확인할 수 있습니다. |
| **읽기 어려움** | 파일 하나가 길어지고 역할이 섞여서, 버그가 났을 때 어디를 봐야 할지 알기 어렵습니다. |

> ⚠️ **유지보수 규칙:** 새 기능을 추가할 때도 `라우터 → 서비스 → 저장소` 방향만 호출합니다.
> 라우터에서 `db.add()`·`select()`를 직접 쓰거나, 저장소에서 검증·HTML 처리를 하지 않습니다.
> 검증 규칙은 `services/post_service.py`의 `_clean()` 한 곳에만 둡니다.

### 2. 다른 DB로 바꾸는 방법

DB 주소는 `app/database.py`에서 **환경변수(environment variable) `DATABASE_URL`**로 읽습니다. 값이 없으면 기본값인 SQLite(`database.db`)를 씁니다. 그래서 **코드를 고치지 않고 환경변수만 바꾸면** 다른 DB로 전환됩니다.

```python
# app/database.py
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database.db'}")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
```

| DB | 추가 설치 패키지 | `DATABASE_URL` 예시 (가짜 값) |
|---|---|---|
| SQLite (기본) | 없음 | `sqlite:///./database.db` |
| PostgreSQL | `psycopg[binary]` | `postgresql+psycopg://your_user:your_password@localhost:5432/study_blog` |
| MySQL | `pymysql` | `mysql+pymysql://your_user:your_password@localhost:3306/study_blog?charset=utf8mb4` |

**전환 절차 (PostgreSQL 예시)**

```bash
# 1. 드라이버(파이썬이 해당 DB와 대화하게 해 주는 패키지) 설치 후 requirements.txt에도 추가
pip install "psycopg[binary]"

# 2. DB 서버에서 빈 데이터베이스(study_blog)를 먼저 만든다 (테이블은 서버가 켜질 때 자동 생성)

# 3. 환경변수로 주소를 넘기고 서버 실행
export DATABASE_URL="postgresql+psycopg://your_user:your_password@localhost:5432/study_blog"
uvicorn app.main:app --reload
```

**주의할 점**

- 접속 주소에는 비밀번호가 들어가므로 **코드나 README에 실제 값을 쓰지 않고**, 환경변수나 `.gitignore`에 등록된 `.env` 파일로만 관리합니다.
- 기존 `database.db`의 글은 새 DB로 **자동으로 옮겨지지 않습니다.** 필요하면 따로 옮겨야 합니다.
- 저장소·서비스·라우터 코드는 그대로 둡니다. SQLAlchemy ORM이 DB 차이를 대신 처리하기 때문입니다.
- 다만 DB마다 동작이 조금 다른 부분이 있습니다. 예를 들어 검색에 쓰는 `contains()`(SQL `LIKE`)는 SQLite에서는 영문 대소문자를 구분하지 않지만 PostgreSQL에서는 구분합니다. 같은 동작을 원하면 `repositories/post_repository.py`에서만 `icontains()`로 바꾸면 됩니다.
- 현재 미션은 필수 패키지 5개만 쓰도록 제한하므로, 드라이버 추가는 이 미션 범위 밖의 확장입니다.

### 3. 모델 연관관계(relationship)를 추가하는 방법

예시: 글 하나에 **댓글 여러 개**가 달리는 **일대다(One-to-Many)** 관계 (`Post 1 : N Comment`)

**① 모델** — `app/models/comment.py` 추가, `app/models/post.py` 수정

```python
# app/models/comment.py
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))   # 어느 글의 댓글인지 (외래키)
    post: Mapped["Post"] = relationship(back_populates="comments")

# app/models/post.py (Post 클래스에 추가)
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",   # 글을 지우면 그 글의 댓글도 함께 삭제
    )
```

- `ForeignKey("posts.id")`: DB 테이블 수준의 연결(외래키)입니다. `comments.post_id`에 `posts.id` 값이 들어갑니다.
- `relationship()`: 파이썬 수준의 연결입니다. `post.comments`로 댓글 목록을, `comment.post`로 글을 바로 꺼낼 수 있습니다.
- `back_populates`: 양쪽 `relationship`이 같은 관계라는 것을 서로 알려 줍니다.
- `app/main.py`에 `from app.models import comment`를 추가해야 `create_all`이 `comments` 테이블을 만듭니다.

**② 마이그레이션(이미 있는 DB의 구조 바꾸기)**

- `Base.metadata.create_all()`은 **없는 테이블만 새로 만들고, 이미 있는 테이블에 컬럼을 추가하지는 않습니다.**
  - `comments`처럼 **새 테이블**을 추가하는 경우: 서버를 다시 켜면 자동으로 만들어집니다.
  - `posts`에 **새 컬럼**(예: `author_id`)을 추가하는 경우: 자동으로 반영되지 않습니다.
- 개발 중이라 데이터가 없어져도 된다면 `database.db`를 지우고 서버를 다시 켜서 테이블을 새로 만듭니다.
- 실제 데이터를 지켜야 한다면 **Alembic**(SQLAlchemy용 마이그레이션 도구)으로 변경 이력을 관리합니다.

```bash
pip install alembic
alembic init migrations                          # 마이그레이션 폴더 생성 (env.py에서 Base.metadata 연결)
alembic revision --autogenerate -m "add comments" # 모델과 DB를 비교해 변경 스크립트 생성
alembic upgrade head                             # DB에 적용
```

**③ 사용 예시** — 레이어 구조는 그대로 따릅니다.

```python
# repositories/comment_repository.py
def save(db: Session, comment: Comment) -> Comment:
    db.add(comment); db.commit(); db.refresh(comment)
    return comment

# services/comment_service.py
def add_comment(db: Session, post_id: int, content: str) -> CommentRead:
    post_service.get_post(db, post_id)       # 없는 글이면 PostNotFoundError
    if not content.strip():
        raise CommentValidationError(...)
    return CommentRead.model_validate(comment_repository.save(db, Comment(post_id=post_id, content=content.strip())))

# routers/post_router.py
@router.post("/{post_id}/comments")
def create_comment(post_id: int, content: str = Form(""), db: Session = Depends(get_db)):
    comment_service.add_comment(db, post_id, content)
    return RedirectResponse(f"/posts/{post_id}", status_code=303)   # PRG 그대로 적용
```

- 상세 화면에 댓글을 보여 주려면 `schemas/post.py`에 `CommentRead`를 만들고 `PostRead`에 `comments: list[CommentRead] = []`를 추가한 뒤, `detail.html`에서 `{% for c in post.comments %}`로 출력합니다.
- 목록 화면에서 글마다 `post.comments`를 읽으면 글 수만큼 쿼리가 추가로 실행됩니다(**N+1 문제**). 저장소에서 `select(Post).options(selectinload(Post.comments))`로 한 번에 불러와 막습니다.

### 4. SSR에서 REST API로 바꿀 때 고려할 점

지금은 **SSR(서버 사이드 렌더링)**: 서버가 Jinja2로 HTML을 완성해서 보냅니다.
REST 방식에서는 서버가 **데이터(JSON)만** 보내고, 화면은 React 같은 **프론트엔드(브라우저 쪽 프로그램)**가 그립니다.

| 항목 | 지금 (SSR) | REST + 프론트엔드 |
|---|---|---|
| 응답 | `TemplateResponse` (HTML) | Pydantic 스키마 → JSON |
| 입력 | HTML 폼 → `Form()` | JSON 본문 → Pydantic 모델 (`PostCreate`) |
| 등록·수정·삭제 후 | `RedirectResponse(303)` (PRG) | 상태 코드로 결과 전달: 등록 `201`, 수정 `200`, 삭제 `204` |
| 없는 글 | `not_found.html` | `404` + `{"detail": "..."}` |
| 검증 실패 | 폼 다시 보여주기 | `400`/`422` + 어떤 칸이 틀렸는지 JSON |
| 화면 이동 | 서버 URL마다 HTML | 클라이언트 라우팅(React Router 등) |
| HTML 이스케이프(XSS 방어) | Jinja2 자동 이스케이프 | 프론트엔드가 담당 (React는 기본 이스케이프) |
| `templates/` 폴더 | 필요 | 제거 (프론트엔드 프로젝트로 이동) |

**바뀌는 것은 라우터뿐입니다.** 서비스와 저장소는 그대로 재사용합니다. 레이어를 나눈 가장 큰 이유가 여기서 드러납니다.

```python
# routers/post_api_router.py (예시)
router = APIRouter(prefix="/api/posts")

class PostCreate(BaseModel):
    title: str
    content: str
    category: str = ""

@router.post("", status_code=201, response_model=PostRead)
def create(body: PostCreate, db: Session = Depends(get_db)):
    try:
        return post_service.create_post(db, body.title, body.content, body.category)   # 같은 서비스 재사용
    except PostValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors)

@router.get("/{post_id}", response_model=PostRead)
def detail(post_id: int, db: Session = Depends(get_db)):
    try:
        return post_service.get_post(db, post_id)
    except PostNotFoundError:
        raise HTTPException(status_code=404, detail="글을 찾을 수 없습니다.")
```

**추가로 고려할 것**

- **CORS(교차 출처 리소스 공유):** 프론트엔드(예: `localhost:5173`)와 API(`localhost:8000`)의 주소가 다르면, 브라우저가 보안 때문에 요청을 막습니다. FastAPI에 기본으로 들어 있는 `CORSMiddleware`로 허용할 주소만 등록합니다. `allow_origins=["*"]`(모두 허용)는 개발 중에만 씁니다.

  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
  ```

- **클라이언트 라우팅:** `/posts/3` 같은 화면 주소는 프론트엔드가 처리합니다. 사용자가 그 주소에서 새로고침하면 서버에 요청이 가므로, 프론트 서버(또는 Nginx)가 모든 화면 주소에 `index.html`을 돌려주도록 설정합니다. API는 `/api/...`로 주소를 분리해 화면 주소와 겹치지 않게 합니다.
- **프론트엔드 빌드·배포:** 프론트엔드는 `npm run build`로 정적 파일(HTML/JS/CSS)을 만들고, Vercel·Netlify·Nginx 등에 따로 올리거나 FastAPI의 `StaticFiles`로 함께 제공합니다. 서버가 두 개가 되므로 배포 절차도 두 개가 됩니다.
- **점진적 전환:** SSR 라우터(`/posts`)와 API 라우터(`/api/posts`)를 동시에 등록할 수 있습니다. 같은 서비스를 쓰기 때문에, 화면을 하나씩 옮기면서 전환할 수 있습니다.
- 로그인이 생기면 인증 방식(쿠키 세션 또는 토큰)과 CSRF 대응도 함께 정해야 합니다. 이 내용은 다음 미션 범위입니다.

## 스크린샷

| 글 목록 | 글 상세 | 입력 검증 |
|---|---|---|
| ![글 목록](docs/screenshots/list.png) | ![글 상세](docs/screenshots/detail.png) | ![입력 검증](docs/screenshots/form-error.png) |

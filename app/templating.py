from pathlib import Path

from fastapi.templating import Jinja2Templates

# 여러 라우터가 같은 템플릿 설정을 쓰도록 한 곳에서 만든다.
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

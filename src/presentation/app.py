from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.infrastructure.database.models import Base
from src.infrastructure.database.session import engine
from src.presentation.routers import legal_entities, objects, documents, archive, settings

Base.metadata.create_all(engine)

app = FastAPI(title="Охрана — управление объектами")

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(legal_entities.router)
app.include_router(objects.router)
app.include_router(documents.router)
app.include_router(archive.router)
app.include_router(settings.router)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

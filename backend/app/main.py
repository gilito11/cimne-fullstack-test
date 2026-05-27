import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import close_driver, ensure_constraints, get_driver
from .routers import auth, buildings, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_driver()
    try:
        ensure_constraints()
    except Exception as exc:
        logger.warning("Could not create constraints (DB may be unreachable yet): %s", exc)
    yield
    close_driver()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="CIMNE Pre-selection Test API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(buildings.router)

    @app.get("/health", tags=["meta"])
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

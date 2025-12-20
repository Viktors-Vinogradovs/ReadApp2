from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import core, texts, qa


def create_app() -> FastAPI:
    app = FastAPI(title="Reading API", version="0.1.0")

    # CORS: allow your Vite dev server
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,      # or ["*"] while developing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(core.router, tags=["core"])
    app.include_router(texts.router, prefix="/texts", tags=["texts"])
    app.include_router(qa.router, prefix="/qa", tags=["qa"])

    return app


app = create_app()

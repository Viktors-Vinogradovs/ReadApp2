from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import core, texts, qa
from .core.logging_config import setup_logging


# Setup structured logging
setup_logging(level="INFO")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Reading API",
        version="1.0.0",
        description="AI-powered reading comprehension app with multi-language support"
    )

    # CORS: allow your Vite dev server
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,      # or ["*"] while developing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Note: GZIP compression removed due to compatibility issues
    # Can be added back later if needed with: pip install python-multipart
    # from starlette.middleware.gzip import GZipMiddleware (note: GZip not GZIP)

    # Routers
    app.include_router(core.router, tags=["core"])
    app.include_router(texts.router, prefix="/texts", tags=["texts"])
    app.include_router(qa.router, prefix="/qa", tags=["qa"])

    return app


app = create_app()

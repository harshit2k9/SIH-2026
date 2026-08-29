import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import close_db_pool, init_db_pool
from app.routers.documents import limiter, router as documents_router
from app.services.storage import ensure_bucket

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Secure Digital Document Management System",
    description="Legal & investigation document ingestion API",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS: lock this down to your actual frontend origin(s) in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.example"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.on_event("startup")
async def on_startup():
    await init_db_pool()
    await ensure_bucket()


@app.on_event("shutdown")
async def on_shutdown():
    await close_db_pool()


app.include_router(documents_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.services.seed_data import seed_initial_data
from app.core.logging import logger
from app.api.portal_routes import router as portal_router
from app.api.agent_routes import router as agent_router
from app.api.demo_routes import router as demo_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed initial data
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
    logger.info(f"{settings.APP_NAME} started successfully.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI Task Worker for Invoice Processing and Ledger Syncing",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(portal_router)
app.include_router(agent_router)
app.include_router(demo_router)

@app.get("/health", summary="Health check endpoint")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)

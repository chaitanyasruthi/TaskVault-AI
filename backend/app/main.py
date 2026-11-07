from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routes.runs import router as runs_router

app = FastAPI(
    title="TaskVault AI",
    description="Secure AI Agent for Isolated Computer Execution",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to TaskVault AI",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-health")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "status": "healthy"
        }

    except Exception as error:
        return {
            "database": "disconnected",
            "error": str(error)
        }


app.include_router(runs_router)
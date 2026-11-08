
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.database import engine
from app.routes.runs import router as runs_router
from app.agent.routes import router as agent_router


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"


# Initialize FastAPI
app = FastAPI(
    title="TaskVault AI",
    description="Secure AI Agent for Isolated Computer Execution",
    version="1.0.0"
)


# Convert request validation errors from HTTP 422 to HTTP 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request",
            "details": [
                {
                    "location": error["loc"],
                    "message": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        }
    )


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Welcome to TaskVault AI",
        "status": "running"
    }


# Health endpoint
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# Database health endpoint
@app.get("/db-health")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "status": "healthy"
        }

    except Exception:
        return {
            "database": "disconnected",
            "status": "unhealthy"
        }


# Register API routers
app.include_router(runs_router)
app.include_router(agent_router)


# Serve project reports
app.mount(
    "/reports",
    StaticFiles(directory=str(REPORTS_DIR)),
    name="reports"
)

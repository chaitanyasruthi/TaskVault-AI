from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AgentRun
from app.schemas import RunCreate, RunResponse
from app.services.celesto_service import execute_in_sandbox

router = APIRouter(prefix="/api/runs", tags=["Runs"])


# Create a run without executing it
@router.post("", response_model=RunResponse, status_code=201)
def create_run(data: RunCreate, db: Session = Depends(get_db)):

    existing = db.query(AgentRun).filter(
        AgentRun.sandbox_name == data.sandbox_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Sandbox name already exists"
        )

    new_run = AgentRun(
        sandbox_name=data.sandbox_name,
        task=data.task,
        status="queued",
        execution_target="celesto_sandbox"
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    return new_run


# Get all runs
@router.get("", response_model=list[RunResponse])
def get_runs(db: Session = Depends(get_db)):

    return db.query(AgentRun).order_by(
        AgentRun.id.desc()
    ).all()


# Get a single run
@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):

    run = db.query(AgentRun).filter(
        AgentRun.id == run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return run


# Execute a task inside Celesto sandbox
@router.post("/execute")
def execute_run(data: RunCreate, db: Session = Depends(get_db)):

    existing = db.query(AgentRun).filter(
        AgentRun.sandbox_name == data.sandbox_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Sandbox name already exists"
        )

    new_run = AgentRun(
        sandbox_name=data.sandbox_name,
        task=data.task,
        status="running",
        execution_target="celesto_sandbox"
    )

    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    try:
        result = execute_in_sandbox(
            data.task,
            data.sandbox_name
        )

        new_run.status = "completed"
        new_run.result = result

        db.commit()
        db.refresh(new_run)

        return {
            "message": "Task executed successfully",
            "run": RunResponse.model_validate(new_run)
        }

    except ValueError as error:

        new_run.status = "failed"
        new_run.result = {
            "error": str(error),
            "security_blocked": True
        }

        db.commit()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        new_run.status = "failed"
        new_run.result = {
            "error": str(error)
        }

        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Celesto execution failed: {error}"
        )

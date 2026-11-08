import uuid
import base64
import shlex

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent.planner import TaskPlanner
from app.agent.command_generator import CommandGenerator

from app.security.plan_validator import PlanValidator
from app.security.audit_logger import log_command
from app.security.command_guard import validate_command

from app.services.celesto_service import execute_in_sandbox
from app.services.persistence_service import SandboxPersistence

from app.database import get_db
from app.models import AgentRun


# ==========================================
# ROUTER CONFIGURATION
# ==========================================

router = APIRouter(
    prefix="/api/agent",
    tags=["AI Agent"]
)

planner = TaskPlanner()
validator = PlanValidator()
command_generator = CommandGenerator()


# ==========================================
# REQUEST MODEL
# ==========================================

class PlanRequest(BaseModel):
    task: str = Field(
        min_length=5,
        max_length=2000
    )


# ==========================================
# GENERATE TASK PLAN
# ==========================================

@router.post("/plan")
def create_task_plan(data: PlanRequest):

    try:
        plan = planner.create_plan(data.task)

        validation = validator.validate_plan(
            plan.user_request,
            plan.steps
        )

        if not validation["approved"]:
            raise HTTPException(
                status_code=400,
                detail=validation["reason"]
            )

        return {
            "message": "Task plan generated successfully",
            "security": validation,
            "plan": plan.model_dump()
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================
# EXECUTE AI AGENT TASK
# ==========================================

@router.post("/execute")
def execute_agent_task(
    data: PlanRequest,
    db: Session = Depends(get_db)
):

    sandbox_name = "sbx-" + uuid.uuid4().hex[:12]

    run = None
    run_id = None

    try:

        # STEP 1: Generate task plan

        plan = planner.create_plan(data.task)

        # STEP 2: Validate task plan

        validation = validator.validate_plan(
            plan.user_request,
            plan.steps
        )

        if not validation["approved"]:
            raise ValueError(validation["reason"])

        # STEP 3: Generate Python program

        program_code = command_generator.generate_program(
            plan.task_type,
            plan.user_request
        )

        if not program_code:
            raise ValueError(
                "No supported Python program for this task"
            )

        # STEP 4: Encode Python program

        encoded_code = base64.b64encode(
            program_code.encode("utf-8")
        ).decode("ascii")

        # STEP 5: Prepare Python command

        python_command = (
            "python3 -c "
            + shlex.quote(
                "exec(__import__('base64').b64decode("
                + repr(encoded_code)
                + "))"
            )
        )

        # STEP 6: Validate generated command

        approved, reason = validate_command(
            python_command
        )

        if not approved:

            log_command(
                sandbox_name,
                python_command,
                "block"
            )

            raise ValueError(
                f"Security blocked command: {reason}"
            )

        # STEP 7: Create database record

        run = AgentRun(
            sandbox_name=sandbox_name,
            task=data.task,
            status="running",
            execution_target="celesto_sandbox"
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        run_id = run.id

        # STEP 8: Save Celesto computer ID immediately

        def save_computer_id(computer_id: str):

            if not computer_id:
                raise RuntimeError(
                    "Celesto did not return a computer ID"
                )

            run.celesto_computer_id = computer_id

            db.commit()
            db.refresh(run)

            print(
                f"Celesto computer ID saved: {computer_id}"
            )

        # STEP 9: Execute inside persistent Celesto sandbox

        execution = execute_in_sandbox(
            python_command,
            sandbox_name,
            on_computer_created=save_computer_id
        )

        # STEP 10: Save execution status

        run.status = execution["status"]

        # STEP 11: Save complete execution result

        run.result = {
            "plan": plan.model_dump(),
            "security": validation,
            "generated_code": program_code,
            "execution": execution
        }

        db.commit()
        db.refresh(run)

        # STEP 12: Return execution result

        return {
            "message": "Python program executed successfully",
            "run_id": run.id,
            "sandbox_name": sandbox_name,
            "celesto_computer_id": run.celesto_computer_id,
            "status": run.status,
            "plan": plan.model_dump(),
            "security": validation,
            "generated_code": program_code,
            "execution": execution
        }

    except ValueError as error:

        db.rollback()

        if run_id is not None:

            failed_run = db.query(AgentRun).filter(
                AgentRun.id == run_id
            ).first()

            if failed_run:

                failed_run.status = "failed"

                failed_run.result = {
                    **(failed_run.result or {}),
                    "error": str(error),
                    "execution_target": "celesto_sandbox"
                }

                db.commit()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        db.rollback()

        if run_id is not None:

            failed_run = db.query(AgentRun).filter(
                AgentRun.id == run_id
            ).first()

            if failed_run:

                failed_run.status = "failed"

                failed_run.result = {
                    **(failed_run.result or {}),
                    "error": str(error),
                    "execution_target": "celesto_sandbox"
                }

                db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {error}"
        )


# ==========================================
# RESUME PERSISTENT SANDBOX
# ==========================================

@router.post("/runs/{run_id}/resume")
def resume_persistent_sandbox(
    run_id: int,
    db: Session = Depends(get_db)
):

    run = db.query(AgentRun).filter(
        AgentRun.id == run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    if not run.celesto_computer_id:
        raise HTTPException(
            status_code=400,
            detail="No Celesto computer ID found for this run"
        )

    computer = None

    try:

        # STEP 1: Attach and resume existing computer

        persistence = SandboxPersistence(
            run.celesto_computer_id
        )

        computer = persistence.resume_sandbox()

        # STEP 2: Verify resumed sandbox

        result = computer.run(
            "echo TASKVAULT_RESUMED"
        )

        if not result.ok:
            raise RuntimeError(
                "Could not verify resumed sandbox"
            )

        return {
            "message": "Persistent sandbox resumed successfully",
            "run_id": run.id,
            "sandbox_name": run.sandbox_name,
            "celesto_computer_id": run.celesto_computer_id,
            "verification": result.stdout.strip(),
            "status": "running"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Sandbox resume failed: {error}"
        )

    finally:

        # STEP 3: Stop again to retain persistent files

        if computer is not None:

            try:
                computer.stop()

            except Exception as cleanup_error:

                print(
                    f"Sandbox stop failed: {cleanup_error}"
                )


# ==========================================
# DELETE PERSISTENT SANDBOX
# ==========================================

@router.delete("/runs/{run_id}/sandbox")
def delete_persistent_sandbox(
    run_id: int,
    db: Session = Depends(get_db)
):

    run = db.query(AgentRun).filter(
        AgentRun.id == run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    if not run.celesto_computer_id:
        raise HTTPException(
            status_code=400,
            detail="No Celesto computer ID found"
        )

    try:

        # STEP 1: Attach to persistent sandbox

        persistence = SandboxPersistence(
            run.celesto_computer_id
        )

        computer = persistence.resume_sandbox()

        # STEP 2: Delete sandbox

        result = persistence.delete_sandbox(computer)

        # STEP 3: Update database

        run.result = {
            **(run.result or {}),
            "persistence": result
        }

        run.status = "deleted"
        run.celesto_computer_id = None

        db.commit()

        return {
            "message": "Persistent sandbox deleted",
            "run_id": run.id,
            "result": result
        }

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Sandbox deletion failed: {error}"
        )


# ==========================================
# GET PERSISTENT SANDBOX DETAILS
# ==========================================

@router.get("/runs/{run_id}/sandbox")
def get_persistent_sandbox(
    run_id: int,
    db: Session = Depends(get_db)
):

    run = db.query(AgentRun).filter(
        AgentRun.id == run_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return {
        "run_id": run.id,
        "sandbox_name": run.sandbox_name,
        "celesto_computer_id": run.celesto_computer_id,
        "task": run.task,
        "status": run.status,
        "persistence_available": bool(
            run.celesto_computer_id
        )
    }

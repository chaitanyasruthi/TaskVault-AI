from app.database import SessionLocal
from app.models import AgentRun


def test_celesto_computer_id_persistence():

    db = SessionLocal()

    try:
        run = AgentRun(
            sandbox_name="sbx-celestotest123",
            celesto_computer_id="celesto-test-123",
            task="Test persistent computer ID",
            status="completed",
            execution_target="celesto_sandbox"
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        saved_run = db.query(AgentRun).filter(
            AgentRun.id == run.id
        ).first()

        assert saved_run.celesto_computer_id == "celesto-test-123"

        db.delete(saved_run)
        db.commit()

    finally:
        db.close()

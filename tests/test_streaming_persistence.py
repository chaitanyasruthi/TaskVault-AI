
from app.database import SessionLocal, Base, engine
from app.models import AgentRun


def test_streaming_metadata_persistence():

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        run = AgentRun(
            sandbox_name="sbx-streamtest123",
            task="Test streaming metadata persistence",
            status="completed",
            execution_target="celesto_sandbox",
            result={
                "execution": {
                    "status": "completed",
                    "output": "Hello World\n",
                    "exit_code": 0,
                    "streaming": {
                        "command_id": "mock-command-123",
                        "stdout": "Hello World\n",
                        "stderr": "",
                        "exit_code": 0,
                        "duration_ms": 250,
                        "timed_out": False
                    }
                }
            }
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        saved_run = db.query(AgentRun).filter(
            AgentRun.id == run.id
        ).first()

        streaming = saved_run.result["execution"]["streaming"]

        assert streaming["command_id"] == "mock-command-123"
        assert streaming["exit_code"] == 0
        assert streaming["timed_out"] is False

        db.delete(saved_run)
        db.commit()

    finally:
        db.close()

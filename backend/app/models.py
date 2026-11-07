from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    JSON,
    func
)

from app.database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)

    sandbox_name = Column(
        String(100),
        unique=True,
        nullable=False
    )

    task = Column(Text, nullable=False)

    status = Column(
        String(30),
        default="queued",
        nullable=False
    )

    execution_target = Column(
        String(50),
        default="celesto_sandbox",
        nullable=False
    )

    result = Column(JSON, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
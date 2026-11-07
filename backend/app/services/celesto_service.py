import os
from pathlib import Path
from dotenv import load_dotenv
from celesto import Computer

from app.security.command_guard import validate_command
from app.security.audit_logger import log_command

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def execute_in_sandbox(command: str, sandbox_name: str):

    approved, reason = validate_command(command)

    if not approved:
        log_command(sandbox_name, command, "block")
        raise ValueError(f"Security blocked command: {reason}")

    log_command(sandbox_name, command, "allow")

    if not os.getenv("CELESTO_API_KEY"):
        raise RuntimeError("Celesto API key not configured")

    computer = Computer(provider="cloud")

    try:
        result = computer.run(command)

        return {
            "status": "completed",
            "output": result.stdout,
            "execution_target": "celesto_sandbox"
        }

    finally:
        computer.delete()

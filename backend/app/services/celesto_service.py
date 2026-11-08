import os
from pathlib import Path
from typing import Callable, Optional

from dotenv import load_dotenv
from celesto import Computer

from app.security.command_guard import validate_command
from app.security.audit_logger import log_command
from app.services.lifecycle_service import SandboxLifecycle
from app.services.streaming_service import execute_streaming


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def execute_in_sandbox(
    command: str,
    sandbox_name: str,
    on_computer_created: Optional[Callable[[str], None]] = None
):

    lifecycle = SandboxLifecycle(sandbox_name)

    computer = None
    computer_id = None
    persistence_status = "not_created"

    output = ""
    exit_code = None
    python_version = None
    streaming_result = None

    # STEP 1: Validate command

    approved, reason = validate_command(command)

    if not approved:
        log_command(sandbox_name, command, "block")
        lifecycle.mark_failed(reason)

        raise ValueError(
            f"Security blocked command: {reason}"
        )

    # STEP 2: Check Celesto API key

    if not os.getenv("CELESTO_API_KEY"):
        lifecycle.mark_failed(
            "Celesto API key not configured"
        )

        raise RuntimeError(
            "Celesto API key not configured"
        )

    try:

        # STEP 3: Initialize persistent Celesto computer

        computer = Computer(
            provider="cloud",
            lifetime="persistent"
        )

        # STEP 4: Explicitly create and start computer

        computer.start()

        # STEP 5: Retrieve actual Celesto computer ID

        computer_id = computer.id

        if not computer_id:
            raise RuntimeError(
                "Celesto computer started but returned no computer ID"
            )

        persistence_status = "running"

        print(
            f"Celesto computer created successfully: {computer_id}"
        )

        # STEP 6: Immediately save computer ID to PostgreSQL

        if on_computer_created:
            on_computer_created(computer_id)

        lifecycle.mark_running()

        # STEP 7: Check Python installation

        check_command = "command -v python3"

        log_command(
            sandbox_name,
            check_command,
            "allow"
        )

        python_check = computer.run(check_command)

        # STEP 8: Install Python if missing

        if not python_check.ok:

            update_command = "sudo -n apt-get update"

            log_command(
                sandbox_name,
                update_command,
                "allow"
            )

            update_result = computer.run(
                update_command,
                timeout=180
            )

            if not update_result.ok:
                raise RuntimeError(
                    f"APT update failed: {update_result.stderr}"
                )

            install_command = (
                "sudo -n apt-get install -y python3"
            )

            log_command(
                sandbox_name,
                install_command,
                "allow"
            )

            install_result = computer.run(
                install_command,
                timeout=180
            )

            if not install_result.ok:
                raise RuntimeError(
                    f"Python installation failed: {install_result.stderr}"
                )

        # STEP 9: Verify Python installation

        version_command = "python3 --version"

        log_command(
            sandbox_name,
            version_command,
            "allow"
        )

        version_result = computer.run(version_command)

        if not version_result.ok:
            raise RuntimeError(
                f"Python verification failed: {version_result.stderr}"
            )

        python_version = version_result.stdout.strip()

        print(
            f"Python runtime available: {python_version}"
        )

        # STEP 10: Execute command using streaming

        streaming_result = execute_streaming(
            computer,
            command,
            sandbox_name
        )

        output = streaming_result["stdout"]
        exit_code = streaming_result["exit_code"]

        # STEP 11: Verify execution

        if streaming_result["timed_out"]:
            raise RuntimeError(
                "Celesto command timed out"
            )

        if exit_code is None:
            raise RuntimeError(
                "Celesto did not return an exit event"
            )

        if exit_code != 0:
            raise RuntimeError(
                streaming_result["stderr"]
                or f"Execution failed with exit code {exit_code}"
            )

        lifecycle.mark_completed()

    except Exception as error:

        lifecycle.mark_failed(str(error))

        raise

    finally:

        # STEP 12: Stop persistent sandbox and retain files

        if computer is not None:

            try:

                computer.stop()

                persistence_status = "stopped"

                lifecycle.mark_cleanup(
                    "stopped_persistent"
                )

                print(
                    f"Persistent sandbox stopped: {sandbox_name}"
                )

            except Exception as cleanup_error:

                persistence_status = "stop_failed"

                lifecycle.mark_cleanup("failed")

                print(
                    f"Sandbox cleanup failed: {cleanup_error}"
                )

    # STEP 13: Return execution details

    return {
        "status": lifecycle.status,
        "output": output,
        "exit_code": exit_code,
        "python_version": python_version,
        "execution_target": "celesto_sandbox",
        "celesto_computer_id": computer_id,
        "persistence_status": persistence_status,
        "streaming": streaming_result,
        "lifecycle": lifecycle.get_report()
    }

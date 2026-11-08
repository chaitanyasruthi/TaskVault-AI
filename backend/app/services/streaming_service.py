from app.security.audit_logger import log_command


def execute_streaming(computer, command: str, sandbox_name: str):
    """
    Execute a command using Celesto streaming events.
    """

    stdout = []
    stderr = []

    exit_code = None
    command_id = None
    duration_ms = None
    timed_out = False

    log_command(
        sandbox_name,
        command,
        "allow"
    )

    for event in computer.run_stream(command, timeout=120):

        if event.type == "started":
            command_id = event.command_id

            print("Command started:", command_id)

        elif event.type == "stdout":
            stdout.append(event.data)
            print("OUTPUT:", event.data, end="")

        elif event.type == "stderr":
            stderr.append(event.data)
            print("ERROR:", event.data, end="")

        elif event.type == "exit":
            exit_code = event.exit_code
            duration_ms = event.duration_ms
            timed_out = event.timed_out

            print("\nExit code:", exit_code)

    return {
        "command_id": command_id,
        "stdout": "".join(stdout),
        "stderr": "".join(stderr),
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "timed_out": timed_out
    }

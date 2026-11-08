
from types import SimpleNamespace

from app.services.streaming_service import execute_streaming


class MockComputer:

    def run_stream(self, command, timeout=30):

        yield SimpleNamespace(
            type="started",
            command_id="mock-command-123"
        )

        yield SimpleNamespace(
            type="stdout",
            data="Hello World\n"
        )

        yield SimpleNamespace(
            type="stderr",
            data=""
        )

        yield SimpleNamespace(
            type="exit",
            exit_code=0,
            duration_ms=250,
            timed_out=False
        )


def test_streaming_execution(monkeypatch):

    computer = MockComputer()

    monkeypatch.setattr(
        "app.services.streaming_service.log_command",
        lambda *args, **kwargs: None
    )

    result = execute_streaming(
        computer,
        "echo Hello World",
        "sbx-mock123456"
    )

    assert result["command_id"] == "mock-command-123"
    assert result["stdout"] == "Hello World\n"
    assert result["stderr"] == ""
    assert result["exit_code"] == 0
    assert result["duration_ms"] == 250
    assert result["timed_out"] is False

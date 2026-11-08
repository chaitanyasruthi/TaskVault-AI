from unittest.mock import MagicMock

from app.services.persistence_service import SandboxPersistence


def test_stop_persistent_sandbox():

    computer = MagicMock()
    computer.stop.return_value = computer

    persistence = SandboxPersistence("celesto-test-123")

    result = persistence.stop_sandbox(computer)

    computer.stop.assert_called_once()

    assert result["status"] == "stopped"
    assert result["files_retained"] is True


def test_resume_persistent_sandbox(monkeypatch):

    computer = MagicMock()

    monkeypatch.setattr(
        "app.services.persistence_service.Computer.get",
        lambda computer_id, provider: computer
    )

    persistence = SandboxPersistence("celesto-test-123")

    resumed = persistence.resume_sandbox()

    computer.resume.assert_called_once()

    assert resumed is computer


def test_delete_persistent_sandbox():

    computer = MagicMock()

    persistence = SandboxPersistence("celesto-test-123")

    result = persistence.delete_sandbox(computer)

    computer.delete.assert_called_once()

    assert result["status"] == "deleted"


import shlex
from celesto import Computer


class SandboxPersistence:

    def __init__(self, computer_id: str):
        if not computer_id:
            raise ValueError("Computer ID is required")

        self.computer_id = computer_id

    def stop_sandbox(self, computer: Computer):
        computer.stop()

        return {
            "computer_id": self.computer_id,
            "status": "stopped",
            "files_retained": True
        }

    def resume_sandbox(self):
        computer = Computer.get(
            self.computer_id,
            provider="cloud"
        )

        computer.resume()
        return computer

    def verify_file(self, computer: Computer, file_path: str):
        safe_path = shlex.quote(file_path)

        result = computer.run(
            f"test -f {safe_path} && echo EXISTS || echo MISSING"
        )

        return result.stdout.strip() == "EXISTS"

    def delete_sandbox(self, computer: Computer):
        computer.delete()

        return {
            "computer_id": self.computer_id,
            "status": "deleted"
        }

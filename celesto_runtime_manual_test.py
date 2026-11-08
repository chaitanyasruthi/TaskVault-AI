from pathlib import Path
from dotenv import load_dotenv
from celesto import Computer
import os

load_dotenv(Path(__file__).resolve().parent / ".env")

if not os.getenv("CELESTO_API_KEY"):
    raise RuntimeError("Celesto API key not configured")

computer = Computer(provider="cloud")

try:
    print("Checking package manager permissions...")

    result = computer.run("id")
    print("Current user:", result.stdout)
    print("Exit code:", result.exit_code)

    result = computer.run("apt-get --version")
    print("APT version:", result.stdout)
    print("APT exit code:", result.exit_code)

finally:
    print("Cleaning up sandbox...")
    computer.delete()
    print("Cleanup completed.")

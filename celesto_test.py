from pathlib import Path
from dotenv import load_dotenv
from celesto import Computer
import os

load_dotenv(Path(__file__).resolve().parent / ".env")

if not os.getenv("CELESTO_API_KEY"):
    raise RuntimeError("Celesto API key not found")

computer = Computer(provider="cloud")

try:
    print("Sandbox created. Running test command...")

    result = computer.run("echo 'Hello from TaskVault AI cloud sandbox!'")

    print("Command output:")
    print(result.stdout)

finally:
    print("Cleaning up sandbox...")
    computer.delete()
    print("Sandbox cleanup completed.")

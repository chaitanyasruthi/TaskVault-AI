from pathlib import Path
from dotenv import load_dotenv
from celesto import Computer
import os

load_dotenv(Path(__file__).resolve().parent / ".env")

if not os.getenv("CELESTO_API_KEY"):
    raise RuntimeError("Celesto API key not found")

computer = Computer(provider="cloud")

try:
    print("Running successful command...")
    result = computer.run("echo Hello TaskVault")

    print("Result:", result)
    print("Result type:", type(result))
    print("Result attributes:", dir(result))

    print("\nRunning intentional failure...")
    result = computer.run(
        "python -c \"raise Exception('Failure test')\""
    )

    print("Failure result:", result)
    print("Failure attributes:", dir(result))

finally:
    print("Cleaning up sandbox...")
    computer.delete()
    print("Cleanup completed.")

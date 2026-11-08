import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"

REQUIRED_JSON_REPORTS = [
    "problem.json",
    "capabilities.json",
    "lifecycle.json",
    "reliability.json",
    "containment.json",
    "failure_policy.json",
    "concurrency.json",
]


def test_required_json_reports_exist():
    for filename in REQUIRED_JSON_REPORTS:
        assert (REPORTS_DIR / filename).is_file(), (
            f"Missing report: {filename}"
        )


def test_required_json_reports_are_valid():
    for filename in REQUIRED_JSON_REPORTS:
        report_path = REPORTS_DIR / filename
        with report_path.open(encoding="utf-8") as file:
            json.load(file)


def test_failure_trace_is_valid_jsonl():
    trace_path = REPORTS_DIR / "failure_trace.jsonl"
    assert trace_path.is_file()

    with trace_path.open(encoding="utf-8") as file:
        records = [json.loads(line) for line in file if line.strip()]

    assert records, "Failure trace is empty"

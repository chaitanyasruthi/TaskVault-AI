
from typing import List
from pydantic import BaseModel


class TaskPlan(BaseModel):
    user_request: str
    task_type: str
    steps: List[str]
    security_risks: List[str]
    status: str = "planned"


class TaskPlanner:

    def create_plan(self, user_request: str) -> TaskPlan:

        if not user_request or len(user_request.strip()) < 5:
            raise ValueError("Task description is too short")

        task = user_request.strip()
        text = task.lower()

        task_type = "general"
        steps = []
        risks = []

        # Programming task
        if any(word in text for word in [
            "program", "code", "python", "hello world",
            "script", "function"
        ]):

            task_type = "programming"

            steps = [
                "Understand the programming requirements",
                "Identify the required programming language",
                "Prepare the program code",
                "Review the code for errors",
                "Execute the program inside Celesto",
                "Verify the program output",
                "Generate an execution report"
            ]

            risks = [
                "Untrusted code execution",
                "Unauthorized filesystem access",
                "Unexpected command execution"
            ]

        # CSV or data analysis task
        elif any(word in text for word in [
            "csv", "data analysis", "dataset",
            "spreadsheet", "data"
        ]):

            task_type = "data_analysis"

            steps = [
                "Identify the input data file",
                "Inspect the dataset structure",
                "Identify columns and data types",
                "Check for missing or invalid values",
                "Perform the requested analysis",
                "Generate a summary report"
            ]

            risks = [
                "Sensitive information exposure",
                "Unexpected file access",
                "Large file resource consumption"
            ]

        # File management task
        elif any(word in text for word in [
            "file", "folder", "directory",
            "organize", "rename"
        ]):

            task_type = "file_management"

            steps = [
                "Identify the target files or directories",
                "Inspect the requested file operations",
                "Validate the target paths",
                "Check for destructive operations",
                "Execute approved operations inside Celesto",
                "Verify the resulting filesystem state",
                "Generate an execution report"
            ]

            risks = [
                "Accidental file deletion",
                "Unauthorized filesystem modification",
                "Path traversal"
            ]

        # General task
        else:

            task_type = "general"

            steps = [
                "Understand the user's request",
                "Identify the required operations",
                "Analyze potential security risks",
                "Prepare a safe execution plan",
                "Validate the plan",
                "Execute approved operations inside Celesto",
                "Generate an execution report"
            ]

            risks = [
                "Unexpected command execution",
                "Unauthorized resource access"
            ]

        return TaskPlan(
            user_request=task,
            task_type=task_type,
            steps=steps,
            security_risks=risks,
            status="planned"
        )

from typing import List


BLOCKED_KEYWORDS = [
    "delete all files",
    "format disk",
    "steal credentials",
    "exfiltrate data",
    "disable security",
    "access host filesystem",
    "read .env",
    "reveal api key",
    "expose password"
]


class PlanValidator:

    def validate_plan(self, user_request: str, steps: List[str]):

        if not user_request or not user_request.strip():
            return {
                "approved": False,
                "reason": "Empty user request"
            }

        if not steps:
            return {
                "approved": False,
                "reason": "Execution plan contains no steps"
            }

        if len(steps) > 20:
            return {
                "approved": False,
                "reason": "Too many execution steps"
            }

        combined_text = (
            user_request + " " + " ".join(steps)
        ).lower()

        for keyword in BLOCKED_KEYWORDS:

            if keyword in combined_text:
                return {
                    "approved": False,
                    "reason": f"Potential security risk: {keyword}"
                }

        return {
            "approved": True,
            "reason": "Plan passed basic keyword checks"
        }

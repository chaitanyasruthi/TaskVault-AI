import re

# Only allow harmless commands for our initial testing.
ALLOWED_COMMANDS = {
    "echo",
    "pwd",
    "whoami",
    "python",
    "python3",
}

BLOCKED_PATTERNS = [
    r"\brm\b",
    r"\bsudo\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\bmkfs\b",
    r"\bdd\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bssh\b",
    r"\bscp\b",
    r"\.env\b",
    r"api[_-]?key",
    r"password",
    r"secret",
]


def validate_command(command: str):
    if not command or len(command) > 2000:
        return False, "Invalid command length"

    normalized = command.strip()

    if any(pattern in normalized for pattern in [";", "&&", "||", "|", ">", "<", "`", "$(", "\n"]):
        return False, "Shell operators are not allowed"

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return False, "Potentially dangerous command detected"

    first_word = normalized.split()[0]

    if first_word not in ALLOWED_COMMANDS:
        return False, "Command is not in the allowlist"

    return True, "Command approved"

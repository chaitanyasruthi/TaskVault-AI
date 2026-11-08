import re
import shlex
import ast
import base64
import binascii


ALLOWED_COMMANDS = {
    "echo",
    "pwd",
    "whoami",
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
    r"\bos\.system\b",
    r"\bsubprocess\b",
    r"\bshutil\.rmtree\b",
    r"\beval\s*\(",
]

SHELL_OPERATORS = [
    ";", "&&", "||", "|", ">", "<", "`", "$(", "\n"
]

ALLOWED_PROGRAMS = {
    '''print("Hello World")
print("Program executed inside Celesto successfully!")''',

    '''a = 10
b = 20
result = a + b
print("First number:", a)
print("Second number:", b)
print("Sum:", result)''',

    '''n = 5
factorial = 1

for i in range(1, n + 1):
    factorial *= i

print("Number:", n)
print("Factorial:", factorial)'''
}


def validate_command(command: str):

    if not isinstance(command, str):
        return False, "Command must be a string"

    if not command or len(command) > 2000:
        return False, "Invalid command length"

    normalized = command.strip()

    if not normalized:
        return False, "Empty command"

    if any(op in normalized for op in SHELL_OPERATORS):
        return False, "Shell operators are not allowed"

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return False, "Potentially dangerous command detected"

    try:
        parts = shlex.split(normalized)
    except ValueError:
        return False, "Invalid command syntax"

    if not parts:
        return False, "Empty command"

    executable = parts[0]

    if executable not in ALLOWED_COMMANDS:
        return False, "Command is not in the allowlist"

    if executable == "python3":

        if len(parts) != 3 or parts[1] != "-c":
            return False, "Only approved Python execution format is allowed"

        wrapper = parts[2]

        prefix = "exec(__import__('base64').b64decode("
        suffix = "))"

        if not wrapper.startswith(prefix) or not wrapper.endswith(suffix):
            return False, "Python command format is not approved"

        encoded_literal = wrapper[len(prefix):-len(suffix)]

        try:
            encoded_value = ast.literal_eval(encoded_literal)

            if not isinstance(encoded_value, str):
                return False, "Invalid Base64 payload"

            decoded_code = base64.b64decode(
                encoded_value,
                validate=True
            ).decode("utf-8")

        except (ValueError, SyntaxError, UnicodeDecodeError, binascii.Error):
            return False, "Invalid or corrupted Python payload"

        if decoded_code not in ALLOWED_PROGRAMS:
            return False, "Python program is not in the approved program list"

    return True, "Command approved"

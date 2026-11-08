
class CommandGenerator:

    def generate_program(self, task_type: str, user_request: str):

        if task_type != "programming":
            return None

        text = user_request.lower()

        if "hello world" in text:
            return '''print("Hello World")
print("Program executed inside Celesto successfully!")'''

        if "addition" in text or "add two numbers" in text:
            return '''a = 10
b = 20
result = a + b
print("First number:", a)
print("Second number:", b)
print("Sum:", result)'''

        if "factorial" in text:
            return '''n = 5
factorial = 1

for i in range(1, n + 1):
    factorial *= i

print("Number:", n)
print("Factorial:", factorial)'''

        return None

# 🚀 TaskVault AI

### Secure AI Agent for Isolated Computer Execution

TaskVault AI is a secure computer-execution platform that uses Celesto cloud sandboxes to execute approved programming tasks in isolated environments.

It provides task planning, command validation, Python runtime provisioning, execution monitoring, persistent sandbox management, and PostgreSQL-based execution tracking.

## ✨ Features

- **Cloud Sandbox Execution:** Executes programming tasks inside isolated Celesto computers.
- **Task Planning:** Generates execution plans based on user requests.
- **Command Validation:** Applies command allowlisting and basic security checks.
- **Python Runtime Provisioning:** Detects and installs Python when required.
- **Execution Streaming:** Captures standard output, errors, exit codes, and execution duration.
- **Persistent Sandboxes:** Supports stopping and resuming existing Celesto computers.
- **Computer ID Persistence:** Stores Celesto computer IDs in PostgreSQL.
- **Sandbox Cleanup:** Supports stopping and deleting persistent computers.
- **Audit Logging:** Records command execution decisions.
- **Execution Tracking:** Maintains run status and results.

## 🏗️ Architecture

```text
             User
               |
               v
        FastAPI Backend
               |
       +-------+--------+
       |                |
       v                v
   Task Planner    Security Validator
       |                |
       +-------+--------+
               |
               v
        Celesto Service
               |
               v
       Celesto Cloud VM
               |
       Python Execution
               |
               v
        Result Collection
               |
       +-------+--------+
       |                |
       v                v
   PostgreSQL       Audit Logs
```

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Sandbox Platform | Celesto |
| Containerization | Docker, Docker Compose |
| API Documentation | Swagger UI |
| Testing | Pytest |

## 📁 Project Structure

```text
TaskVault-AI/
│
├── backend/
│   └── app/
│       ├── agent/
│       ├── routes/
│       ├── security/
│       ├── services/
│       ├── database.py
│       ├── models.py
│       └── main.py
│
├── reports/
│   ├── problem.json
│   ├── capabilities.json
│   ├── lifecycle.json
│   ├── reliability.json
│   ├── containment.json
│   ├── failure_policy.json
│   ├── failure_trace.jsonl
│   ├── concurrency.json
│   └── postmortem.md
│
├── logs/
├── seeds/
├── tests/
├── demo/
│
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── pytest.ini
└── README.md
```

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.12+
- Docker Desktop
- Docker Compose
- Celesto API account and API key

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd TaskVault-AI
```

### 2. Configure Environment Variables

Create a local `.env` file:

```bash
cp .env.example .env
```

Configure your environment variables:

```env
DATABASE_URL=postgresql+psycopg://taskvault:taskvault_dev_password@db:5432/taskvault
CELESTO_API_KEY=your_celesto_api_key
```

Never commit `.env` or expose your API key.

### 3. Start the Application

```bash
docker compose up -d --build
```

### 4. Check Container Status

```bash
docker compose ps
```

### 5. Open Swagger Documentation

```text
http://localhost:8000/docs
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check application

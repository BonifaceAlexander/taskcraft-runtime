# User Guide: Building Your Own Agent 🤖

This guide shows you how to create a custom "Coworker Agent" using TaskCraft.

## 1. Prerequisites
*   Python 3.12+
*   Google Gemini API Key
*   (Optional) Docker Desktop (for Sandboxing)
*   (Optional) Postgres Database (for Scalability)

## 2. Installation
```bash
git clone https://github.com/your-username/taskcraft
cd taskcraft
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 3. Creating Your Agent
Example: A "Weather Assistant" defined in YAML.

### Step 3a: Define Custom Skills
Create `my_skills.py`:
```python
from taskcraft.tools.decorators import retryable_tool

@retryable_tool()
async def check_weather(city: str) -> str:
    return f"The weather in {city} is Sunny."
```

### Step 3b: Configuration (`weather_agent.yaml`)
```yaml
name: "Weather Assistant"
description: "Checks weather for me."
objective: "Check the weather in London."
tools:
  - module: "my_skills"
policies:
  max_actions: 5
```

## 4. Running the Agent (Dual Modes) 🚀

TaskCraft  supports **Computer Use**.

### Mode A: Desktop / Personal
Best for "Organizing my computer" or "Vision Tasks".
*   **Backend**: SQLite
*   **Executor**: Local Process
*   **Feature**: Can see your screen!

**Command**:
```bash
# Verify environment
make install

# Run the Desktop Worker
make run
```
*   *Note*: Ensure `taskcraft.tools.desktop` is in your YAML `tools`.

### Mode B: Enterprise / Cloud
Best for heavy workloads, untrusted code, or complex logical reasoning.
*   **Backend**: Postgres
*   **Executor**: Docker Sandbox (now supports `run_python`)
*   **Planner**: Tree of Thoughts (ToT)

```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/taskcraft"
python -m taskcraft.main_cli run \
  -f examples/incident_reporter.yaml \
  --backend postgres \
  --executor docker \
  --planner tot
```

## 5. Observability & Control

### Check Status
```bash
python -m taskcraft.main_cli status <TASK_ID>
```

### View Logs
```bash
python -m taskcraft.main_cli logs <TASK_ID>
```

### Approve a Blocked Task
If an agent hits a policy block (e.g., "Approval Required"), it pauses.
```bash
python -m taskcraft.main_cli approve <TASK_ID>
```

# TaskCraft: The Agent Runtime 🏗️

**TaskCraft is infrastructure for building reliable AI coworkers.**

It is a runtime that provides **state**, **governance**, and **execution primitives** so you can trust LLMs with real work.

## 🌟 The Vision: "Universal Worker"
TaskCraft is a **superset** of tools like "Claude Computer Use".
*   **Desktop Mode:** It runs locally to manage your files, apps, and terminal.
*   **Enterprise Mode:** It runs in the cloud to process tickets, emails, and data.
*   **Connectors:** If you have a Python function for it (Salesforce, Slack, Jira), TaskCraft can use it.

## What is TaskCraft?

TaskCraft turns an LLM into a governed system that can:

1.  **Define a Role**: "You are an Ops Analyst", defined in code/config.
2.  **Execute Work**: "Run this workflow", not "Chat with me".
3.  **Persist State**: Resume after failure, track progress (SQLite backed).
4.  **Enforce Safety**: "Ask approval before sending emails" (Policy Engine).
5.  **Observe**: Detailed audit logs of every thought and action.

## The Goal

A user of TaskCraft should be able to trust an AI system with real operational work — because it behaves like a governed coworker, not an unpredictable assistant.

## Quickstart

### 1. Installation

```bash
pip install -e .
# Ensure you have the latest SDK
pip install google-genai
export GOOGLE_API_KEY="your-key-here"
```

### 2. Define Your Coworker (`ops_analyst.yaml`)

Define abilities and **governance rules** declaratively.

```yaml
name: "Ops Analyst"
objective: "Summarize weekly incidents and email the team."

tools:
  - module: "examples.incident_tools" 

policies:
  approval_required:
    - "send_report" # STOP! Human review needed.
```

### 3. Run the Task

**Local Mode (Default):**
Uses SQLite and runs tools on your host machine.
```bash
python -m taskcraft.main_cli run -f examples/incident_reporter.yaml
```

**Enterprise Mode:**
Uses Postgres, Docker Sandboxing, and Advanced Planning.
```bash
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/db"
python -m taskcraft.main_cli run \
  -f examples/incident_reporter.yaml \
  --backend postgres \
  --executor docker \
  --planner tot
```

**Output:**
```
🚀 Starting task...
🤖 Backend: postgres | Executor: docker
...
```

### 4. Governance (The "Human Layer")

The agent **cannot** proceed without you. This is a feature.

```bash
# View the blocked task
python -m taskcraft.main_cli approve <task_id>
```
**Output:**
```
✅ Approving task...
📧 SENDING EMAIL to manager@corp.com ...
🏁 Task finished.
```

## Architecture

*   **Runtime**: The `AgentRuntime` executes the loop (Plan -> Policy -> Action).
*   **State**: `SQLiteStateManager` ensures durability. If the process dies, the task resumes where it left off.
*   **Policy**: `PolicyEngine` intercepts tools before execution.
*   **Tools**: Any Python function can be a tool.

## Documentation
*   [User Guide](docs/user_guide.md) - How to build and run agents.
*   [Technical Architecture](docs/architecture.md) - Deep dive into Planner/Executor/Runtime.
*   [Project Structure](docs/project_structure.md) - Codebase map.
*   [Deployment Guide](docs/deployment.md) - Cloud Run / K8s instructions.
*   [Design Decisions](docs/DESIGN_DECISIONS.md) - Why we built it this way.
*   [Security Policy](docs/SECURITY.md) - Governance and safety.
*   [Contributing](docs/CONTRIBUTING.md) - Developer guide.

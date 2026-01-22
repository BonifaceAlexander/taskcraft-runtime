# TaskCraft: The Gemini Consumer Runtime

![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)

**Taskcraft is an open execution and governance runtime for building reliable, multi-step AI coworkers. It currently runs on Google Gemini and is designed to be extended to other models over time.**

Unlike simple chat loops, TaskCraft provides **durable state**, **policy governance**, **observability**, and **lifecycle management**.

## 🚀 Quickstart Guide

### prerequisites
*   Python 3.10+
*   A Google Gemini API Key

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-username/taskcraft.git
cd taskcraft

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package
pip install -e .
```

### 2. Configuration

Export your Gemini API key:

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

### 3. Usage

#### Interactive "Coworker" Run
Run a task. The agent will plan, check policies, and execute tools.

```bash
python -m taskcraft.main_cli run "Write a poem about rust and save it to poem.txt"
```

#### Simulating Governance (The "Risky" Action)
Try a task that triggers a safety policy (configured to block `deploy_prod`):

```bash
python -m taskcraft.main_cli run "Deploy version v2 to production"
```

**Output:**
```
🚀 Starting task: Deploy version v2 to production
...
✋ Task halted. Use 'taskcraft approve <task_id>' to continue.
```

#### Approving a Task
Copy the `task_id` from the output above and approve it:

```bash
python -m taskcraft.main_cli approve <task_id>
```
The agent will now resume, execute the restricted action, and complete the task.

## 🏗 Architecture

TaskCraft introduces the missing primitives for AI work:

*   **Agent Runtime**: A formal state machine (`IDLE`, `PLANNING`, `EXECUTING`, `AWAITING_APPROVAL`).
*   **Persistence**: SQLite-backed state. If the process crashes, the agent remembers where it was.
*   **Governance Engine**: Policies that run *before* every tool execution.
*   **Tool Abstraction**: Retry logic (`tenacity`) and safe execution wrappers.

## 🤝 Contributing

We aim to eventually propose this as a runtime layer for the official `gemini-cli`.
Project structure:

*   `src/taskcraft/core`: Main runtime logic.
*   `src/taskcraft/governance`: Policy definitions.
*   `src/taskcraft/state`: DB and Data Models.

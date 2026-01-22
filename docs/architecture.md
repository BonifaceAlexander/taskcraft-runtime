# TaskCraft Architecture 🏗️

TaskCraft is designed as a **modular runtime** for autonomous agents, separating the "Decision Engine" (LLM) from the "Execution Engine" (Tools & State).

```mermaid
graph TD
    User[User / CLI] -->|Objective| R[Agent Runtime]
    
    subgraph "TaskCraft Runtime"
        R -->|State| SM[State Manager (SQLite)]
        R -->|Plan| LLM[Gemini Adapter]
        R -->|Action| PE[Policy Engine]
        PE -->|Safe?| T[Tool Executor]
        T -->|Result| SM
    end
    
    T -->|FileSystem| FS[Local Files]
    T -->|API| Ext[External Services]
```

## Core Components

### 1. Agent Runtime (`core/runtime.py`)
The heart of the system. It runs the **ReAct Loop**:
1.  **Observe**: Fetch history from State Manager.
2.  **Think**: Send history to Gemini to get the next step.
3.  **Governance**: Check if the proposed step is safe via Policy Engine.
4.  **Act**: Execute the tool.
5.  **Reflect**: Store the result and repeat.

### 2. State Manager (`state/persistence.py`)
*   Uses **SQLite** (`aiosqlite`) for durable storage.
*   Stores `Tasks`, `Steps`, and `Artifacts`.
*   Allows pausing/resuming agents (process-restartable).

### 3. Policy Engine (`governance/policy.py`)
*   **Interceptor Pattern**: Runs *before* every tool execution.
*   **Rules**:
    *   `MaxActionsPolicy`: Prevents infinite loops.
    *   `ApprovalRequiredPolicy`: Blocks "sensitive" tools (e.g., `delete_file`) until human approval.

### 4. Config System (`config/`)
*   **Declarative Agents**: Agents defined in YAML (`agent.yaml`).
*   **Dynamic Loading**: Tools can be imported from any Python module at runtime.

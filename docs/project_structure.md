# Project Structure 📂

Each module in TaskCraft has a specific responsibility. Here is a guide to the codebase:

```text
src/taskcraft/
├── config/             # YAML Loading & Schema Validation
│   ├── loader.py       # Reads agent.yaml and imports tools
│   └── schema.py       # Pydantic models for configuration
│
├── core/               # The "Brain" of the runtime
│   ├── lifecycle.py    # Enums (AgentState: PENDING, RUNNING, BLOCKED)
│   └── runtime.py      # Main loop (Orchestrator)
│
├── governance/         # Safety & Control Layer
│   └── policy.py       # Classes for preventing dangerous actions
│
├── planner/            # "Thinking" Modules
│   ├── base.py         # Planner Protocol
│   ├── gemini.py       # Standard Gemini implementation
│   └── tot.py          # Tree of Thoughts implementation
│
├── executor/           # "Doing" Modules
│   ├── base.py         # Executor Protocol
│   ├── local.py        # Host process execution
│   └── docker.py       # Sandboxed container execution
│
├── state/              # Memory & Persistence
│   ├── models.py       # Data classes (Task, Step)
│   ├── persistence.py  # SQLite database wrapper
│   └── postgres.py     # Postgres backend
│
├── tools/              # Capabilities
│   ├── definitions.py  # Basic built-ins (read/write file)
│   ├── fs_skills.py    # Advanced file skills (scan, move, summarize)
│   ├── desktop.py      # Computer Use (Screen Capture)
│   └── decorators.py   # @retryable_tool wrapper
│
└── main_cli.py         # The entrypoint (argparse)
```

## Key Files for Contributors
*   **Adding Tools**: Add a function in `tools/` and register it in your YAML.
*   **Changing Models**: Check `planner/gemini.py`.
*   **New Policies**: Inherit from `Policy` in `governance/policy.py`.

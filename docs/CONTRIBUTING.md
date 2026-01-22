# Contributing to TaskCraft

We welcome contributions! Please follow these guidelines to keep the runtime robust.

## 1. Philosophy
*   **Infrastructure, not Features:** We build the rails, not the trains.
*   **Test-Driven:** If it's not tested, it doesn't exist.
*   **Type-Safe:** All code must be fully typed (Python 3.12+).

## 2. Development Setup
We standardized the workflow using a `Makefile`.

```bash
# Install dependencies (including dev tools)
make install
```

## 3. Running Tests
```bash
make test
```

## 4. Project Structure (Standard)
*   `taskcraft/planner/`: LLM integration implementations.
*   `taskcraft/executor/`: Tool execution logic.
*   `taskcraft/governance/`: Policy rules.
*   `taskcraft/state/`: Database models.

## 5. Pull Request Process
1.  Open an Issue describing the fix/feature.
2.  Create a branch.
3.  Add unit tests covering your change.
4.  Verify `pytest` passes.
5.  Submit PR.

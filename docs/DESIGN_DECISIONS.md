# Architecture & Design Decisions

This document records the trade-offs and rationale behind the TaskCraft architecture.

## 1. Runtime vs. Agent Framework
**Decision:** Build a *runtime* (infrastructure), not an *agent framework* (prompt library).
**Rationale:**
*   Enterprises need **predictability** (governance, persistence) more than "clever" prompting.
*   Prompt engineering is brittle and model-specific. Infrastructure is durable.
*   We focus on the *execution loop*, *state management*, and *policy enforcement*.

## 2. SQLite for State Persistence
**Decision:** Use `aiosqlite` (SQLite) for the default state backend.
**Rationale:**
*   **Zero-dependency deployment**: No need to spin up Postgres to test.
*   **Single-file portability**: Easy to archive debug tasks by copying the `.db` file.
*   **Performance**: Sufficient for single-worker runtimes (which is the recommended pattern per agent).
*   *Future*: The `StateManager` abstraction allows swapping for Postgres/Redis later.

## 3. Protocol-Based Planner
**Decision:** Use a Python `Protocol` for the `Planner` instead of hardcoding Gemini.
**Rationale:**
*   While we are "Gemini-First", we must be "Model-Agnostic" in design.
*   Allows easy mocking for unit tests (no API calls).
*   Allows potential future support for local models (Gemma).

## 4. Policy as Interceptors
**Decision:** The `PolicyEngine` intercepts `execute()` calls rather than relying on the LLM to "behave".
**Rationale:**
*   **Zero Trust**: We assume the LLM *will* hallucinate or try disallowed actions.
*   Hard constraints (code) > Soft constraints (system prompts).

## 5. Explicit "Approve" Step in CLI
**Decision:** Approval is an asynchronous State transition, not a runtime prompt input.
**Rationale:**
*   Blocking main thread for `input()` is bad for servers.
*   The agent halts (persists state) and dies.
*   Approval is a separate process (CLI command or API call) that resumes the state.
*   This enables "human-in-the-loop" without "human-waiting-at-the-keyboard".

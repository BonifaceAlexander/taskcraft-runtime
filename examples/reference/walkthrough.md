# TaskCraft Reference Walkthrough

This guide demonstrates the core lifecycle of a TaskCraft agent: **Plan -> Execute -> Policy Gate -> Resume**.

**Scenario**: An "Ops Analyst" agent needs to fetch incident logs and email a summary to a manager.

## 1. Task Definition
We define the agent in `incident_reporter.yaml`:
```yaml
objective: "Read incidents for week '2026-W03', summarize, and send report."
policies:
  approval_required: ["send_report"]
```

## 2. Execution (Step-by-Step)

### A. Start the Agent
Run the agent from the CLI.
```bash
python -m taskcraft.main_cli run -f examples/reference/incident_reporter.yaml
```

**What happens:**
1.  **Planner** (Gemini) sees the objective and calls `fetch_incidents(week="2026-W03")`.
2.  **Runtime** executes the tool and returns the mock logs.
3.  **Planner** analyzes the logs and decides to call `send_report(summary="...", recipient="manager@...")`.

### B. Policy Gate (Governance)
The `send_report` tool is protected. The Policy Engine intercepts the call.

**Log Output:**
```
🤖 Agent decides to call: send_report
🛡️ POLICY INTERCEPT: Approval Required for 'send_report'
✋ Task halted. Use 'taskcraft approve <task_id>' to continue.
```
*The process exits. The state is saved in SQLite.*

## 3. Human Approval (Resume)
The user reviews the pending action and approves it.

```bash
python -m taskcraft.main_cli approve <task_id>
```

**What happens:**
1.  **State Manager** loads the frozen task.
2.  **Runtime** verifies the pending step requires approval.
3.  **Runtime** executes `send_report`.

**Log Output:**
```
✅ Approving step: send_report
📧 SENDING EMAIL to manager@corp.com ...
[Summary Content...]
🏁 Task finished with status: COMPLETED
```

## 4. Why this matters
This creates a **collaborative loop**. The AI does the heavy lifting (fetching, reasoning, summarizing), but the human retains final authority over high-stakes actions (emailing, deploying, deleting).

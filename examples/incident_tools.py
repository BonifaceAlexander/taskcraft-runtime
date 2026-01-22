from typing import List
from taskcraft.tools.decorators import retryable_tool

@retryable_tool()
async def fetch_incidents(week: str) -> str:
    """Fetches incident logs for a specific week."""
    # Mock data for demonstration
    if week == "2026-W03":
        return """
        INCIDENT LOG 2026-W03:
        1. [CRITICAL] DB-01 Replication Lag (20ms -> 5000ms). Root cause: Network congestion.
        2. [WARN] API-Gateway 5xx spike (2%). Root cause: Bad deploy v2.1.
        3. [INFO] User registration dropped by 5% (Marketing campaign ended).
        """
    return "No incidents found."

@retryable_tool()
async def send_report(summary: str, recipient: str) -> str:
    """Sends the summary report via email/slack."""
    # In reality, this would use SMTP or Slack API
    print(f"📧 SENDING EMAIL to {recipient} 📧")
    print("-" * 30)
    print(summary)
    print("-" * 30)
    return "Report sent successfully."

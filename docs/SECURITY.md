# Security Policy 🔒

TaskCraft is designed to execute code and modify systems. Security is paramount.

## 1. Tool Sandboxing
*   **Current State:** Tools run in the same process as the runtime.
*   **Risk:** A malicious tool or hallucinated parameter could access the host environment.
*   **Mitigation:** 
    *   Use `PolicyEngine` to allowlist tools.
    *   Deploy in containerized environments (Docker) with limited scope/mounts.

## 2. API Key Management
*   **Rule:** Never commit API keys to code.
*   **Mechanism:** TaskCraft uses `os.getenv("GOOGLE_API_KEY")`.
*   **Recommendation:** Use Secret Managers (AWS Secrets Manager, Google Secret Manager) to inject these at runtime in production.

## 3. Human-in-the-loop Governance
*   Policy: `ApprovalRequiredPolicy`
*   Mechanism: Critical tools (e.g., `write_prod`, `send_email`) should ALWAYS require approval.
*   The runtime enforced hard-stops on these tools.

## 4. Reporting Vulnerabilities
Please do not report security issues in public issues. 
Email: security@example.com (Replace with real contact)

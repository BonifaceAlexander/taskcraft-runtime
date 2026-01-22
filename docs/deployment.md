# Deploying TaskCraft to the Cloud ☁️

TaskCraft is designed as a **stateless compute workload** with **stateful persistence**. This makes it easy to run on any cloud platform.

## 1. Containerize the Agent
We provide a `Dockerfile` out of the box.

```bash
# Check Dockerfile ensures 'google-genai' is installed
docker build -t taskcraft-agent:latest .
```

## 2. Strategies

### Option A: Serverless Worker (Cloud Run / AWS Fargate)
Best for: On-demand agents (e.g., triggered by a webhook or schedule).

*   **Trigger**: Use a Cloud Scheduler to run the container every Monday at 9 AM.
*   **State**: Mount a persistent volume (EFS / Cloud Storage FUSE) to `/app/data` to keep the SQLite DB, or switch the `StateManager` to use a managed DB (Postgres).
*   **Command**:
    ```bash
    # Example for Google Cloud Run
    gcloud run jobs deploy ops-analyst \
      --image taskcraft-agent:latest \
      --set-env-vars GOOGLE_API_KEY=secret_key \
      --command python -m taskcraft.main_cli run -f examples/incident_reporter.yaml
    ```

### Option B: Long-Running Service (Kubernetes / EC2)
Best for: Agents that need to listen for events or require complex approval workflows.

*   **Deployment**: Run as a Deployment in K8s.
*   **Persistence**: Use a PersistentVolumeClaim (PVC) for the state DB.
*   **Observability**: Logs are written to stdout (JSON format), ready for Datadog/CloudWatch.

## 3. Handling Permissions (Governance)
In the cloud, you can't manually type "y" to approve.

*   **Pattern**: Separation of Concerns.
*   **Worker**: The agent runs in the cloud. When it hits a blocked tool, it pauses and saves state to the shared DB.
*   **Approver**: A separate protected service (or a CLI tool on your laptop connected to the same DB) lists blocked tasks and issues approvals.

## 4. Environment Variables
Ensure these are set in your cloud environment:
*   `GOOGLE_API_KEY`: For the LLM.
*   `PYTHONPATH`: Set to `/app/src`.
*   `SQLITE_DB_PATH`: Path to the persistent storage volume.

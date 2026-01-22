# Base Image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (build tools for some packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY src/ src/
COPY examples/ examples/

# Install dependencies and the package itself
RUN pip install --no-cache-dir -e .

# Create directory for persistent state (SQLite)
# In production, mount a volume here
RUN mkdir -p /app/data
ENV SQLITE_DB_PATH=/app/data/taskcraft.db

# Output buffering off for logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Default entrypoint: Run the CLI
ENTRYPOINT ["python", "-m", "taskcraft.main_cli"]

# Default command (can be overridden)
CMD ["run", "-f", "examples/incident_reporter.yaml"]

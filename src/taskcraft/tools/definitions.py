from pathlib import Path
from taskcraft.tools.decorators import retryable_tool

@retryable_tool()
async def write_file(path: str, content: str) -> str:
    """Safe tool: Writes content to a file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Successfully wrote {len(content)} bytes to {path}"

@retryable_tool()
async def read_file(path: str) -> str:
    """Safe tool: Reads content from a file."""
    p = Path(path)
    if not p.exists():
        return f"Error: File {path} does not exist."
    return p.read_text()

@retryable_tool()
async def deploy_prod(version: str) -> str:
    """Risky tool: Simulates a deployment."""
    # This tool should be gated by policy
    return f"Deployed version {version} to PRODUCTION."

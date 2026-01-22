import structlog
import docker
from typing import Dict, Any
from taskcraft.executor.base import Executor

logger = structlog.get_logger()

class DockerExecutor(Executor):
    """
    Executes tools inside an isolated Docker container.
    Safe for untrusted tools or code execution.
    """
    def __init__(self, image: str = "python:3.12-slim", timeout: int = 30):
        self.client = docker.from_env()
        self.image = image
        self.timeout = timeout
        
        # Ensure image exists
        try:
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            logger.info("Pulling docker image", image=image)
            self.client.images.pull(image)

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the tool logic inside a container.
        Note: This is a simplified implementation. Real-world sandboxing requires
        serializing the tool function and arguments, injecting them into the container,
        running them, and capturing the output.
        """
        logger.info("Executing tool in Docker", tool=tool_name, image=self.image)
        
        try:
            # For demonstration, we assume 'params' contains a 'command' or 'script' 
            # if the tool is generic like "run_shell". 
            # Mapping Python functions to Docker calls requires a specific protocol.
            # Here we just execute a simple command if possible, or fail for complex Python objects.
            
            # Simplified: IF the tool is a shell command wrapper
            if tool_name == "run_shell" and "command" in params:
                command = params["command"]
                container = self.client.containers.run(
                    self.image,
                    command=["/bin/sh", "-c", command],
                    detach=True,
                    mem_limit="128m",
                    network_disabled=True 
                )
                
                exit_code = container.wait(timeout=self.timeout)
                logs = container.logs().decode("utf-8")
                container.remove()
                
                if exit_code['StatusCode'] == 0:
                    return {"status": "SUCCESS", "output": logs}
                else:
                    return {"status": "ERROR", "error": logs}
            
            # Improved Python Execution Sandbox
            if tool_name == "run_python" and "code" in params:
                code = params["code"]
                # Wrap code to print output to stdout so we can capture it
                # We use a simple wrapper that execs the code
                wrapped_code = f"""
import sys
try:
{code}
except Exception as e:
    print(f"ERROR: {{e}}")
"""
                # Run python -c "..."
                # Note: Escaping quotes is tricky. Better to write to a temp file in the container.
                # For MVP, we pass it as a single string if simple, or assume 'script' file.
                
                # Better approach: Write code to file inside container then run
                cmd = f"python3 -c '{code}'" 
                
                container = self.client.containers.run(
                    self.image,
                    command=["python3", "-c", code],
                    detach=True,
                    mem_limit="128m",
                    network_disabled=True 
                )
                
                exit_code = container.wait(timeout=self.timeout)
                logs = container.logs().decode("utf-8")
                container.remove()

                if exit_code['StatusCode'] == 0:
                    return {"status": "SUCCESS", "output": logs}
                else:
                    return {"status": "ERROR", "error": logs}

            # Fallback for complex tools
            return {"status": "ERROR", "error": f"DockerExecutor: Tool '{tool_name}' not supported or protocol mismatch."}
            
        except Exception as e:
            logger.error("Docker execution failed", error=str(e))
            return {"status": "ERROR", "error": str(e)}

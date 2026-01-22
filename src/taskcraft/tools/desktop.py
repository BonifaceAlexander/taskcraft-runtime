import structlog
import subprocess
import os
import platform
from datetime import datetime
from taskcraft.tools.decorators import retryable_tool

logger = structlog.get_logger()

@retryable_tool()
async def capture_screen(output_path: str = None) -> str:
    """
    Captures a screenshot of the current screen.
    Returns the path to the image file, formatted for the Planner to use.
    """
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"screenshot_{timestamp}.png"
    
    # Ensure absolute path
    output_path = os.path.abspath(output_path)
    
    system = platform.system()
    
    try:
        if system == "Darwin": # macOS
            # -x: mute sound
            # -r: do not add shadow
            cmd = ["screencapture", "-x", "-r", output_path]
        elif system == "Linux":
            # Assume gnome-screenshot or scrot
            cmd = ["gnome-screenshot", "-f", output_path]
        else:
            return "Error: Screen capture only supported on macOS/Linux (with gnome-screenshot)"

        logger.info("Capturing screen", output=output_path)
        subprocess.run(cmd, check=True)
        
        if os.path.exists(output_path):
            # Return in the format the Planner expects
            return f"Screenshot saved. [IMAGE: {output_path}]"
        else:
            return "Error: Screenshot command ran but file not found."
            
    except Exception as e:
        logger.error("Screen capture failed", error=str(e))
        return f"Error capturing screen: {str(e)}"

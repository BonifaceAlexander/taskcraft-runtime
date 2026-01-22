import os
import shutil
import hashlib
from typing import List, Dict, Optional
from datetime import datetime
from taskcraft.tools.decorators import retryable_tool

@retryable_tool()
async def list_directory(path: str, recursive: bool = False) -> str:
    """
    Lists files in a directory.
    Args:
        path: The directory path to scan.
        recursive: If True, scans subdirectories.
    """
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."
    
    files_info = []
    try:
        if recursive:
            for root, dirs, files in os.walk(path):
                for file in files:
                    full_path = os.path.join(root, file)
                    size = os.path.getsize(full_path)
                    files_info.append(f"{full_path} (Size: {size}b)")
        else:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isfile(full_path):
                    size = os.path.getsize(full_path)
                    files_info.append(f"{item} (Size: {size}b)")
                else:
                    files_info.append(f"{item}/ (DIR)")
                    
        return "\n".join(files_info) if files_info else "Directory is empty."
    except Exception as e:
        return f"Error scanning directory: {str(e)}"

@retryable_tool()
async def read_file_snippet(path: str, max_chars: int = 2000) -> str:
    """
    Reads the first N characters of a text file to understand its content.
    """
    if not os.path.exists(path):
        return f"Error: File '{path}' not found."
        
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(max_chars)
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@retryable_tool()
async def move_file(src: str, dest_folder: str) -> str:
    """
    Moves a file to a destination folder. Creates the folder if it doesn't exist.
    """
    if not os.path.exists(src):
        return f"Error: Source '{src}' not found."
    
    try:
        # Create dest dir if needed
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            
        filename = os.path.basename(src)
        dest_path = os.path.join(dest_folder, filename)
        
        # Avoid collisions
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%H%M%S")
            new_filename = f"{base}_{timestamp}{ext}"
            dest_path = os.path.join(dest_folder, new_filename)
            
        shutil.move(src, dest_path)
        return f"Moved '{src}' -> '{dest_path}'"
    except Exception as e:
        return f"Error moving file: {str(e)}"

@retryable_tool()
async def append_to_summary(summary_file: str, entry: str) -> str:
    """
    Appends a line to the summary index.
    """
    try:
        with open(summary_file, 'a', encoding='utf-8') as f:
            f.write(entry + "\n")
        return "Summary updated."
    except Exception as e:
        return f"Error writing summary: {str(e)}"

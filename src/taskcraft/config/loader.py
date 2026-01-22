import yaml
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, Callable
from taskcraft.config.schema import AgentConfig

def load_config(path: str) -> AgentConfig:
    """Loads and validates the agent configuration from YAML."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(p, "r") as f:
        data = yaml.safe_load(f)
        
    return AgentConfig(**data)

def load_tools(config: AgentConfig) -> Dict[str, Callable]:
    """
    Dynamically loads tools based on the configuration.
    Supports built-in tools (by name) and custom modules.
    """
    tools = {}
    
    # 1. Load Built-ins (simple registry for now)
    from taskcraft.tools.definitions import write_file, read_file, deploy_prod
    builtins = {
        "write_file": write_file,
        "read_file": read_file,
        "deploy_prod": deploy_prod
    }
    
    for tool_cfg in config.tools:
        # A. Built-in
        if tool_cfg.name and tool_cfg.name in builtins:
            tools[tool_cfg.name] = builtins[tool_cfg.name]
            
        # B. Custom Module (Dynamic Import)
        if tool_cfg.module:
            try:
                mod = importlib.import_module(tool_cfg.module)
                # Find all async functions in module
                for name, obj in inspect.getmembers(mod):
                    if (inspect.isfunction(obj) or inspect.iscoroutinefunction(obj)):
                         # Filter: Only load functions defined IN this module, not imports
                         if obj.__module__ == mod.__name__:
                             tools[name] = obj
            except ImportError as e:
                print(f"Warning: Could not import module {tool_cfg.module}: {e}")

    return tools

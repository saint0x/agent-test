import os
from pathlib import Path

def root(start_path=None):
    """Find the project root by looking for the butterfly.config.py file."""
    if start_path is None:
        start_path = os.getcwd()
    
    current_path = Path(start_path).resolve()
    while True:
        if (current_path / 'butterfly.config.py').exists():
            return current_path
        if current_path.parent == current_path:
            return None
        current_path = current_path.parent

def create_config_file(project_root):
    """Create the butterfly.config.py file at the project root."""
    config_path = project_root / 'butterfly.config.py'
    if not config_path.exists():
        with config_path.open('w') as f:
            f.write(f"PROJECT_ROOT = r'{project_root}'\n")
            f.write("\ndef get_project_root():\n    return PROJECT_ROOT\n")
            f.write("\nSCAN_INTERVAL = 3600  # Time between scans in seconds\n")
            f.write("IGNORE_PATTERNS = ['.git', 'node_modules', 'venv']  # Directories to ignore during scans\n")
    return config_path

def load_config():
    """Load the configuration from butterfly.config.py."""
    project_root = root()
    if not project_root:
        raise FileNotFoundError("butterfly.config.py not found in this or any parent directory")
    
    config_path = project_root / 'butterfly.config.py'
    config = {}
    with config_path.open() as f:
        exec(f.read(), config)
    
    return config

def update_config(key, value):
    """Update a configuration value in butterfly.config.py."""
    project_root = root()
    if not project_root:
        raise FileNotFoundError("butterfly.config.py not found in this or any parent directory")
    
    config_path = project_root / 'butterfly.config.py'
    with config_path.open('r+') as f:
        content = f.read()
        if f"{key} = " in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"{key} = "):
                    lines[i] = f"{key} = {repr(value)}"
                    break
            f.seek(0)
            f.write('\n'.join(lines))
            f.truncate()
        else:
            f.seek(0, 2)
            f.write(f"\n{key} = {repr(value)}\n")
PROJECT_ROOT = r'/workspaces/butterfly'

def get_project_root():
    return PROJECT_ROOT

SCAN_INTERVAL = 3600  # Time between scans in seconds
IGNORE_PATTERNS = ['.git', 'node_modules', 'venv']  # Directories to ignore during scans

import os
from dotenv import load_dotenv, set_key

def load_env_file(project_root):
    """Load the .env file from the project root."""
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)

def get_api_key():
    """Retrieve the Butterfly API key from the environment variables."""
    return os.getenv('BUTTERFLY_API_KEY')

def set_api_key(project_root, api_key):
    """Set the Butterfly API key in the .env file."""
    env_path = os.path.join(project_root, '.env')
    set_key(env_path, 'BUTTERFLY_API_KEY', api_key)
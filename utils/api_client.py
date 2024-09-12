import requests
from .api_key_manager import validate_api_key

class ButterflyAPIClient:
    def __init__(self, api_key, base_url="https://api.butterfly.ai"):
        self.base_url = base_url
        self.api_key = api_key

    def validate_api_key(self):
        # First, check if the API key is valid in our local database
        if not validate_api_key(self.api_key):
            return False
        
        # If it's valid locally, we can also check with the server
        try:
            response = requests.get(
                f"{self.base_url}/validate",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
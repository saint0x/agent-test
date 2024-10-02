import logging
import httpx
import asyncio
import subprocess
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Function to start the FastAPI server
async def start_server():
    logger.info("Starting FastAPI server...")
    process = subprocess.Popen(["python3", "api-generation/main.py"])
    await asyncio.sleep(1)
    return process

# Function to authenticate the API key
async def authenticate_api_key(api_key):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://127.0.0.1:3005/authenticate?api_key={api_key}")
        if response.status_code == 200:
            logger.info("✅ API key authenticated successfully.")
        else:
            logger.error(f"❌ API key authentication failed: {response.text}")
            os._exit(1)  # Exit the script if authentication fails

if __name__ == "__main__":
    
    server_process = asyncio.run(start_server())
    # Prompt for API key input
    api_key = input("Please enter the API key to authenticate: ")
    asyncio.run(authenticate_api_key(api_key))
   
    server_process.terminate()  # Terminate the server after authentication

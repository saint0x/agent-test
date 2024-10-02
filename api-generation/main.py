from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
import logging
import socket

from .utils.db_utils import create_tables, get_user, insert_user, delete_user
from .utils.auth_utils import authenticate_user  # type: ignore
from .utils.rate_limit_utils import RateLimiter
from .utils.cors_utils import CORSConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Function to find an open port
def find_open_port(start_port=3000, end_port=4000):
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('0.0.0.0', port)) != 0:
                return port
    raise RuntimeError("No available ports found")

# Use lifespan for startup and shutdown events
async def lifespan(app: FastAPI):
    logger.info("🚀 Backend is starting...")
    create_tables()  # Ensure tables are created on startup
    yield
    logger.info("🛑 Backend is shutting down...")

app = FastAPI(lifespan=lifespan)  # Pass lifespan to the FastAPI app

# Setup rate limiting
rate_limiter = RateLimiter()
rate_limiter.setup_limiter(app)

# Setup CORS
CORSConfig(app)  # Create an instance of CORSConfig

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic model for API key
class APIKey(BaseModel):
    api_key: str

@app.get("/")
async def root():
    logger.info("🌍 Root endpoint accessed")
    return {"message": "API is running"}

@app.post("/api_key")
async def create_api_key(api_key: str = Query(...)):  # Use Query to require the api_key
    if get_user(api_key):
        logger.error("❌ API key already exists.")
        raise HTTPException(status_code=400, detail="API key already exists.")
    insert_user(api_key)  # Insert the API key into the database
    logger.info(f"✅ API key {api_key} created successfully.")
    return {"message": "API key created successfully."}

@app.delete("/api_key")
async def delete_api_key(api_key: str = Query(...)):
    delete_user(api_key)
    logger.info(f"✅ API key {api_key} deleted successfully.")
    return {"message": "API key deleted successfully."}

@app.get("/authenticate")
async def authenticate(api_key: str = Depends(oauth2_scheme)):
    keys = authenticate_user(api_key)
    if keys:
        logger.info("✅ API key authenticated successfully.")
        return {"message": "API key is valid"}
    else:
        logger.error("❌ API key authentication failed.")
        raise HTTPException(status_code=401, detail="Invalid API key")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = find_open_port()
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host=host, port=port)

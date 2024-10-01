from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
import os
import sys
import logging  # Import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import create_tables, get_user, insert_user  # type: ignore
from auth_utils import User, verify_password, get_password_hash, authenticate_user, UserCreate  # type: ignore
from jwt_utils import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, Token  # type: ignore
from rate_limit_utils import RateLimiter  # Updated import
from cors_utils import CORSConfig  # Updated import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Use lifespan for startup and shutdown events
async def lifespan(app: FastAPI):
    logger.info("🚀 Backend is starting...")
    create_tables()
    yield
    logger.info("🛑 Backend is shutting down...")

app = FastAPI(lifespan=lifespan)  # Pass lifespan to the FastAPI app

# Setup rate limiting
rate_limiter = RateLimiter()  # Create an instance of RateLimiter
rate_limiter.setup_limiter(app)  # Call setup_limiter on the app

# Setup CORS
CORSConfig(app)  # Create an instance of CORSConfig

@app.get("/")
async def root():
    logger.info("🌍 Root endpoint accessed")  # Log with emoji
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)

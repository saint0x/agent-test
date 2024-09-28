from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import timedelta
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_generation.db_utils import create_tables, get_user, insert_user # type: ignore
from api_generation.auth_utils import User, verify_password, get_password_hash, authenticate_user # type: ignore
from api_generation.jwt_utils import create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES # type: ignore
from api_generation.rate_limit_utils import setup_limiter, rate_limit # type: ignore
from api_generation.cors_utils import setup_cors # type: ignore

app = FastAPI()

# Setup rate limiting
setup_limiter(app)

# Setup CORS
setup_cors(app)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/register")
@rate_limit("3/minute")
async def register_user(username: str, password: str):
    if get_user(username):
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    insert_user(username, hashed_password)
    return {"message": "User registered successfully"}

@app.post("/token", response_model=Token)
@rate_limit("5/minute")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    token_data = decode_token(token)
    user = get_user(token_data.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username}

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
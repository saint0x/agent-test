from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from db_utils import get_user
from models import User  # Updated import
from jwt_utils import decode_token  # Import decode_token
from pydantic import BaseModel  # Ensure this import is included

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):  # Access hashed_password from the dictionary
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    token_data = decode_token(token)
    user = get_user(username=token_data.username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

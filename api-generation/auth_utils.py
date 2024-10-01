from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from db_utils import get_user  # Updated import
from pydantic import BaseModel  # Ensure this import is included

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    api_key: str


def authenticate_user(api_key: str):
    user = get_user(api_key)
    if not user:
        return False
    return user


async def get_current_user(api_key: str = Depends(oauth2_scheme)):
    user = get_user(api_key)
    if user is None:
        raise HTTPException(status_code=401, detail="API key not found")
    return user

# File: api-generation/models.py

from pydantic import BaseModel

class User(BaseModel):
    username: str
    hashed_password: str

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Dict
# Pydantic Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatMessage(BaseModel):
    sender: str  # "user" or "bot"
    text: str
    timestamp: datetime = datetime.now()

class Chat(BaseModel):
    user: str
    messages: List[ChatMessage]


class UserDB(BaseModel):
    name: str
    email: EmailStr
    hashed_password: str
    previous_chats: List[Dict[str, str]] = []  # List of dicts with chat ID and title



from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Dict
from bson import ObjectId
import schema.models as models
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import re
# App Initialization
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "chatbotDB"
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# JWT Configuration
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # Ensure correct token URL


# Utility Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request) -> Dict:
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    
    if token and token.startswith("Bearer "):
        token = token.split("Bearer ")[1]  # Extract the actual token
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



@app.get("/auth/check")
async def check_auth(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return {"message": "Authenticated", "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/signup")
async def signup(user: models.UserCreate, response: Response):
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "previous_chats": []
    }
    result = await db.users.insert_one(new_user)

    access_token = create_access_token({"sub": str(result.inserted_id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="Lax")

    return {"message": "Signup successful"}


@app.post("/login")
async def login(response: Response, login_data: models.UserCreate):
    print(login_data)
    db_user = await db.users.find_one({"email": login_data.email})  # Use email field

    if not db_user or not verify_password(login_data.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user["_id"])}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="Lax")

    return {"message": "Login successful"}



@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@app.post("/start_chat")
async def start_chat(user: dict = Depends(get_current_user)):
    """Create a new chat session with a default title 'Chat'"""

    chat = {
        "users": [user["_id"]],
        "messages": [],
        "title": "Chat"  # Set default title
    }

    result = await db.chats.insert_one(chat)
    chat_id = str(result.inserted_id)

    return {"chat_id": chat_id, "title": "Chat"}

# from fastapi import FastAPI, Request, Depends
# from bson import ObjectId
# from datetime import datetime
# import motor.motor_asyncio
from doctor_agent import get_next_question, generate_diagnosis

@app.post("/save_chat")
async def save_chat(request: Request):
    """Handles chat, asking one question at a time, then generates diagnosis."""
    chat_data = await request.json()
    chat_id = chat_data["chat_id"]
    message = chat_data["message"]

    chat_object_id = ObjectId(chat_id)

    # Fetch chat session
    chat = await db.chats.find_one({"_id": chat_object_id})
    if not chat:
        return {"error": "Chat not found"}

    # Save user message to database
    await db.chats.update_one(
        {"_id": chat_object_id},
        {"$push": {"messages": {
            "sender": message["sender"],
            "text": message["text"],
            "timestamp": datetime.fromisoformat(message["timestamp"])
        }}}
    )

    # Get chat history
    chat_history = chat["messages"]

    # Check if we need to ask another question or generate the final diagnosis
    next_question = get_next_question(chat_history)

    if next_question:
        # Ask the next question
        bot_response = {"sender": "bot", "text": next_question, "timestamp": datetime.now().isoformat()}
    else:
        # Gather patient responses for final diagnosis
        user_responses = {
            msg["text"]: chat_history[i + 1]["text"] if i + 1 < len(chat_history) else "N/A"
            for i, msg in enumerate(chat_history)
            if msg["sender"] == "bot"
        }
        
        symptoms = chat_history[0]["text"]  # First user message = initial symptom
        diagnosis = generate_diagnosis(symptoms, user_responses)

        bot_response = {"sender": "bot", "text": diagnosis, "timestamp": datetime.now().isoformat()}

    # Save bot response
    await db.chats.update_one(
        {"_id": chat_object_id},
        {"$push": {"messages": bot_response}}
    )

    return {"message": "Message saved successfully", "llm_response": bot_response}


@app.post("/end_chat")
async def end_chat(request: Request, user: dict = Depends(get_current_user)):
    """Mark chat as completed and add it to user's previous chats with a title"""
    chat_data = await request.json()

    # Debugging: Print received data
    print("Received chat data:", chat_data)  

    if "chat_id" not in chat_data:
        return JSONResponse({"error": "Missing chat_id in request"}, status_code=400)

    chat_id = chat_data["chat_id"]
    chat_object_id = ObjectId(chat_id)

    chat = await db.chats.find_one({"_id": chat_object_id})
    if not chat:
        return JSONResponse({"error": "Chat not found"}, status_code=404)

    # Extract a meaningful title, e.g., first message or default name
    chat_title = chat_data.get("title") or chat.get("title") or "Untitled Chat"

    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$push": {"previous_chats": {"chat_id": chat_id, "title": chat_title}}}
    )

    return {"message": "Chat ended successfully", "chat_id": chat_id, "title": chat_title}



@app.get("/chats", response_model=list[models.Chat])
async def get_user_chats(user: dict = Depends(get_current_user)):
    """Retrieve all previous chats for a user"""
    
    # Extract chat IDs and titles from `previous_chats`
    chat_entries = user.get("previous_chats", [])
    
    valid_chats = []
    for entry in chat_entries:
        if isinstance(entry, dict) and "chat_id" in entry:
            chat_id = entry["chat_id"]
            title = entry.get("title", "Untitled Chat")  # Default title if missing
            if ObjectId.is_valid(chat_id):
                valid_chats.append({"chat_id": ObjectId(chat_id), "title": title})

    # Retrieve chat details from the database
    chat_objects = await db.chats.find({"_id": {"$in": [c["chat_id"] for c in valid_chats]}}).to_list(length=100)

    # Construct response with chat title
    return [
        models.Chat(
            user=str(chat["users"][0]),
            title=next((c["title"] for c in valid_chats if c["chat_id"] == chat["_id"]), "Untitled Chat"),
            messages=[
                models.ChatMessage(
                    sender=m["sender"], 
                    text=m["text"], 
                    timestamp=m["timestamp"]
                ) for m in chat["messages"]
            ]
        ) for chat in chat_objects
    ]

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Generator
from sqlalchemy.orm import Session
from database.database import SessionLocal, User, engine
from dotenv import load_dotenv

# Dependency to open and close DB connection for each request
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# load .env file
load_dotenv()

# Load security from .env, fallback to default if missing for development
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key-for-dev-12345678")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Function create token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# function create refresh token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function identify token for APIs safety
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    # token from Cookie
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

app = FastAPI(title="Eagle Data Tool Backend API")

@app.on_event("startup")
async def startup_event():
    print("INFO: Server is starting...")

# CORS configuration for React to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PYDANTIC MODELS (Define input/output data) ---
class UserCreate(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


# --- API ENDPOINTS ---

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Data Tool Backend is running!"}

@app.post("/api/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # 1. Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists!")
    
    # 2. Hash password using bcrypt
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
    
    # 3. Create new user
    new_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Sign up successfully!", 
        "user_id": new_user.id, 
        "email": new_user.email,
        "name": f"{new_user.first_name} {new_user.last_name}",
        "credits": new_user.credits
    }

@app.post("/api/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Find user in DB
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not exist!")
    
    # check password by using bcrypt
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Wrong password!")
        
    # create token   
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})

    # Return cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,       
        max_age=15*60,         
        samesite="lax",      
        secure=False        
    )
    # set refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,       
        max_age=7*24*60*60,         
        samesite="lax",      
        secure=False        
    )
    return {
        "message": "Login successfully!",
        "user_id": db_user.id,
        "email": db_user.email,
        "name": f"{db_user.first_name} {db_user.last_name}",
        "credits": db_user.credits,
    }

@app.post("/api/refresh")
def refresh_token(request: Request, response: Response):
    # get refresh_token from cookie
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
            
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
            
        new_access_token = create_access_token(data={"sub": email})
        
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            max_age=15 * 60,
            samesite="lax",
            secure=False
        )
        return {"message": "Token refreshed successfully"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.get("/api/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    # Trả về thông tin hồ sơ của người dùng đang đăng nhập
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "credits": current_user.credits
    }
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from datetime import timedelta
from database.models import User
from database.config import get_db
from backend.services.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: str

class Token(BaseModel):
    access_token: str
    token_type: str

# POST /auth/register
@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.id}, expires_delta=timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}

# POST /auth/login
@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.id}, expires_delta=timedelta(hours=24))
    return {"access_token": access_token, "token_type": "bearer"}

# GET /auth/me
@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }
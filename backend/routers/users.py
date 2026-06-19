from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session
from database.models import User
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# Pydantic schemas
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

# GET /users
@router.get("/", response_model=list[UserResponse])
async def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return [{"id": user.id, "email": user.email, "created_at": user.created_at.isoformat()} for user in users]

# GET /users/{id}
@router.get("/{id}", response_model=UserResponse)
async def get_user(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "email": user.email, "created_at": user.created_at.isoformat()}

# PUT /users/{id}
@router.put("/{id}", response_model=UserResponse)
async def update_user(id: str, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.email:
        user.email = user_update.email
    if user_update.password:
        user.password = hash_password(user_update.password)
    
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "created_at": user.created_at.isoformat()}

# DELETE /users/{id}
@router.delete("/{id}", status_code=204)
async def delete_user(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None
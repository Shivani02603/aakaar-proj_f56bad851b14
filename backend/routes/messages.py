from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import Message as MessageModel
from database.config import get_db

router = APIRouter(prefix="/api/sessions/{session_id}/messages", tags=["Messages"])

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    session_id: UUID

class MessageResponse(MessageBase):
    id: UUID
    created_at: str

@router.post("/", response_model=MessageResponse)
async def create_message(session_id: UUID, message_data: MessageCreate, db: Session = Depends(get_db)):
    new_message = MessageModel(**message_data.dict())
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.get("/")
async def get_session_messages(session_id: UUID, db: Session = Depends(get_db)):
    messages = db.query(MessageModel).filter(MessageModel.session_id == session_id).all()
    return messages
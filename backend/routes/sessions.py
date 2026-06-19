from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import Session as SessionModel
from database.config import get_db

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

class SessionBase(BaseModel):
    name: str

class SessionCreate(SessionBase):
    user_id: UUID

class SessionResponse(SessionBase):
    id: UUID
    created_at: str

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    new_session = SessionModel(**session_data.dict())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/")
async def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).all()
    return sessions

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
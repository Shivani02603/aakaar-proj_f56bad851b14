from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel, Field
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import UploadedFile as UploadedFileModel
from database.config import get_db

router = APIRouter(prefix="/api/sessions/{session_id}/files", tags=["Files"])

class UploadedFileBase(BaseModel):
    filename: str
    file_size: int

class UploadedFileCreate(UploadedFileBase):
    session_id: UUID

class UploadedFileResponse(UploadedFileBase):
    id: UUID
    uploaded_at: str

@router.post("/", response_model=UploadedFileResponse)
async def upload_file(session_id: UUID, file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = f"/uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    file_size = len(file.file.read())
    new_file = UploadedFileModel(session_id=session_id, filename=file.filename, file_path=file_path, file_size=file_size)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

@router.get("/")
async def list_files(session_id: UUID, db: Session = Depends(get_db)):
    files = db.query(UploadedFileModel).filter(UploadedFileModel.session_id == session_id).all()
    return files
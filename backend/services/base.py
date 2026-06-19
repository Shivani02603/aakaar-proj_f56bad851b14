from typing import Type, TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

# Type variables for generic CRUD service
ModelType = TypeVar("ModelType")

class CRUDService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, obj_in: ModelType) -> ModelType:
        try:
            db.add(obj_in)
            db.commit()
            db.refresh(obj_in)
            return obj_in
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating {self.model.__name__}: {str(e)}")

    def read(self, db: Session, id: str) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return obj

    def read_all(self, db: Session) -> List[ModelType]:
        try:
            return db.query(self.model).all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Error reading {self.model.__name__}: {str(e)}")

    def update(self, db: Session, id: str, obj_in: dict) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        try:
            for key, value in obj_in.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating {self.model.__name__}: {str(e)}")

    def delete(self, db: Session, id: str) -> None:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        try:
            db.delete(obj)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting {self.model.__name__}: {str(e)}")
import uuid
from sqlalchemy.exc import SQLAlchemyError
from database.models import User, Session, UploadedFile, DocumentChunk, Message
from database.config import SessionLocal

def seed_database():
    session = SessionLocal()
    try:
        # Insert Users
        user1 = User(id=uuid.uuid4(), email="user1@example.com")
        user2 = User(id=uuid.uuid4(), email="user2@example.com")
        user3 = User(id=uuid.uuid4(), email="user3@example.com")
        session.add_all([user1, user2, user3])
        session.commit()

        # Insert Sessions
        session1 = Session(id=uuid.uuid4(), user_id=user1.id, name="Session 1")
        session2 = Session(id=uuid.uuid4(), user_id=user2.id, name="Session 2")
        session.add_all([session1, session2])
        session.commit()

        # Insert Uploaded Files
        file1 = UploadedFile(
            id=uuid.uuid4(),
            session_id=session1.id,
            filename="file1.pdf",
            file_path="/path/to/file1.pdf",
            file_size=1024,
        )
        file2 = UploadedFile(
            id=uuid.uuid4(),
            session_id=session2.id,
            filename="file2.docx",
            file_path="/path/to/file2.docx",
            file_size=2048,
        )
        session.add_all([file1, file2])
        session.commit()

        # Insert Messages
        message1 = Message(
            id=uuid.uuid4(),
            session_id=session1.id,
            role="user",
            content="Hello, this is a test message.",
        )
        message2 = Message(
            id=uuid.uuid4(),
            session_id=session2.id,
            role="assistant",
            content="This is a response message.",
        )
        session.add_all([message1, message2])
        session.commit()

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error seeding database: {e}")
    finally:
        session.close()
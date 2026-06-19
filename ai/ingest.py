import os
import pandas as pd
from typing import List, Dict
from .embeddings import get_embedding
from sqlalchemy import create_engine, text

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def chunk(document: str) -> List[str]:
    """
    Splits a document into overlapping chunks using the recursive strategy.
    """
    tokens = document.split()
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk = " ".join(tokens[start:end])
        chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def ingest_excel(file_path: str, session_id: str, user_id: str):
    """
    Reads an Excel file, chunks its content, generates embeddings, and upserts into the vector store.
    """
    # Read database connection string from environment variable
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    # Connect to the PostgreSQL database
    engine = create_engine(db_url)

    # Read the Excel file
    excel_data = pd.ExcelFile(file_path)

    for sheet_name in excel_data.sheet_names:
        sheet_data = excel_data.parse(sheet_name)
        document = sheet_data.to_string(index=False)

        # Chunk the document
        chunks = chunk(document)

        # Generate embeddings for each chunk
        embeddings = [get_embedding(chunk) for chunk in chunks]

        # Upsert embeddings into the vector store
        with engine.connect() as connection:
            for i, embedding in enumerate(embeddings):
                query = text("""
                    INSERT INTO vector_store (session_id, user_id, chunk_id, embedding, sheet_name)
                    VALUES (:session_id, :user_id, :chunk_id, :embedding, :sheet_name)
                    ON CONFLICT (session_id, chunk_id)
                    DO UPDATE SET embedding = EXCLUDED.embedding;
                """)
                connection.execute(query, {
                    "session_id": session_id,
                    "user_id": user_id,
                    "chunk_id": f"{sheet_name}_{i}",
                    "embedding": embedding,
                    "sheet_name": sheet_name
                })
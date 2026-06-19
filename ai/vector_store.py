import os
import psycopg2
from typing import List, Dict, Any

def get_pg_connection():
    """
    Lazily initialize and return a PostgreSQL connection.
    """
    db_host = os.getenv("PG_HOST")
    db_port = os.getenv("PG_PORT", "5432")
    db_name = os.getenv("PG_DATABASE")
    db_user = os.getenv("PG_USER")
    db_password = os.getenv("PG_PASSWORD")

    if not all([db_host, db_name, db_user, db_password]):
        raise ValueError("One or more PostgreSQL environment variables are not set.")

    connection = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    return connection

def upsert(id: str, vector: List[float], metadata: Dict[str, Any]):
    """
    Upsert a vector and its metadata into the pgvector table.
    """
    connection = get_pg_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                embedding VECTOR(%s),
                metadata JSONB
            );
        """, (len(vector),))
        connection.commit()

        cursor.execute("""
            INSERT INTO vectors (id, embedding, metadata)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET embedding = EXCLUDED.embedding,
                metadata = EXCLUDED.metadata;
        """, (id, vector, metadata))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def search(query_embedding: List[float], top_k: int, **filters) -> List[Dict[str, Any]]:
    """
    Search for the top-k most similar vectors in the pgvector table.
    """
    connection = get_pg_connection()
    cursor = connection.cursor()

    try:
        filter_clauses = []
        filter_values = []
        for key, value in filters.items():
            filter_clauses.append(f"metadata ->> %s = %s")
            filter_values.extend([key, value])

        filter_query = " AND ".join(filter_clauses) if filter_clauses else "TRUE"

        cursor.execute(f"""
            SELECT id, metadata, 1 - (embedding <=> %s) AS similarity
            FROM vectors
            WHERE {filter_query}
            ORDER BY embedding <=> %s
            LIMIT %s;
        """, [query_embedding, query_embedding, top_k] + filter_values)

        results = cursor.fetchall()
        matches = [{"id": row[0], "metadata": row[1], "similarity": row[2]} for row in results]
        return matches
    finally:
        cursor.close()
        connection.close()
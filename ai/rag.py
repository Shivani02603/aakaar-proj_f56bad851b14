import os
from .embeddings import get_embedding
from sqlalchemy import create_engine, text
import requests

def retrieve_context(query: str, top_k: int, session_id: str, user_id: str) -> List[Dict]:
    """
    Embeds the query, retrieves the top-k relevant chunks from the vector store.
    """
    # Read database connection string from environment variable
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    
    # Connect to the PostgreSQL database
    engine = create_engine(db_url)

    # Generate embedding for the query
    query_embedding = get_embedding(query)

    # Retrieve top-k chunks by cosine similarity
    with engine.connect() as connection:
        query = text("""
            SELECT chunk_id, sheet_name, embedding
            FROM vector_store
            WHERE session_id = :session_id AND user_id = :user_id
            ORDER BY (embedding <-> :query_embedding) ASC
            LIMIT :top_k;
        """)
        result = connection.execute(query, {
            "session_id": session_id,
            "user_id": user_id,
            "query_embedding": query_embedding,
            "top_k": top_k
        })
        return [{"chunk_id": row["chunk_id"], "sheet_name": row["sheet_name"], "embedding": row["embedding"]} for row in result]

def answer_question(query: str, session_id: str, user_id: str) -> Dict:
    """
    Retrieves context, builds a prompt, and generates an answer using the runtime LLM.
    """
    # Retrieve context
    context_chunks = retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)

    # Build the prompt
    context_text = "\n".join([chunk["chunk_id"] for chunk in context_chunks])
    prompt = f"Context:\n{context_text}\n\nQuestion: {query}\nAnswer:"

    # Read LLM API key from environment variable
    llm_api_key = os.getenv("GEMINI_API_KEY")
    if not llm_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Call the runtime LLM
    response = requests.post(
        "https://api.google.com/gemini-2.0-flash/generate",
        headers={"Authorization": f"Bearer {llm_api_key}"},
        json={"prompt": prompt}
    )
    response_data = response.json()

    # Extract answer and sources
    answer = response_data.get("answer", "")
    sources = [{"chunk_id": chunk["chunk_id"], "sheet_name": chunk["sheet_name"]} for chunk in context_chunks]

    return {"answer": answer, "sources": sources}
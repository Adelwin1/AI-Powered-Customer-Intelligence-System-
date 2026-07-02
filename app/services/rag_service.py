import json
from app.services.embedding_service import embed_text
from app.core.database import SessionLocal
from app.models.ticket import Ticket


# -------------------------
# STORE TICKET WITH EMBEDDING
# -------------------------
def process_ticket(ticket_id: int):
    db = SessionLocal()

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        db.close()
        return None

    # create embedding (local, no OpenAI needed)
    vector = embed_text(ticket.title + " " + ticket.description)

    # store as JSON string (MVP approach)
    ticket.embedding = json.dumps(vector.tolist())

    db.commit()
    db.close()

    return ticket


# -------------------------
# SEMANTIC SEARCH (CORE RAG STEP)
# -------------------------
def retrieve_context(question: str, limit: int = 5):
    db = SessionLocal()

    tickets = db.query(Ticket).all()

    query_vec = embed_text(question)

    scored = []

    for t in tickets:
        if not t.embedding:
            continue

        try:
            vec = json.loads(t.embedding)
        except:
            continue

        # cosine similarity manually
        import numpy as np

        a = np.array(query_vec)
        b = np.array(vec)

        score = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        scored.append((t, score))

    db.close()

    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:limit]


# -------------------------
# ASK QUESTION (FULL RAG)
# -------------------------
def ask_question(question: str):
    from app.services.ai_response_service import generate_response

    results = retrieve_context(question)

    return generate_response(question, results)
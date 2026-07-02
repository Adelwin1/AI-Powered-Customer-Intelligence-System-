from app.services.rag_service import retrieve_context
from app.services.action_engine import apply_action
from app.core.database import SessionLocal


def ticket_agent(query: str):
    db = SessionLocal()

    results = retrieve_context(query)

    if not results:
        return {
            "status": "no_match",
            "answer": "No similar tickets found.",
            "confidence": 0.0
        }

    ticket, score = results[0]

    # decision logic
    if score > 0.85:
        action = "auto_resolve"
    elif score > 0.65:
        action = "suggest_resolution"
    else:
        action = "escalate"

    # APPLY ACTION (this is the upgrade)
    updated_ticket = apply_action(ticket, action)

    db.add(updated_ticket)
    db.commit()
    db.refresh(updated_ticket)
    db.close()

    return {
        "action_taken": action,
        "confidence": float(score),
        "ticket": {
            "id": updated_ticket.id,
            "status": updated_ticket.status,
            "priority": updated_ticket.priority,
            "resolution": updated_ticket.resolution
        }
    }
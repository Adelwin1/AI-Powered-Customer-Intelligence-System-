from app.core.database import SessionLocal
from app.models.ticket import Ticket


def get_system_stats():
    db = SessionLocal()

    tickets = db.query(Ticket).all()

    total = len(tickets)

    open_tickets = len([t for t in tickets if t.status == "open"])
    resolved = len([t for t in tickets if t.status == "resolved"])
    escalated = len([t for t in tickets if t.status == "escalated"])

    categories = {}

    for t in tickets:
        cat = t.category or "unknown"
        categories[cat] = categories.get(cat, 0) + 1

    db.close()

    return {
        "total_tickets": total,
        "open": open_tickets,
        "resolved": resolved,
        "escalated": escalated,
        "category_distribution": categories
    }
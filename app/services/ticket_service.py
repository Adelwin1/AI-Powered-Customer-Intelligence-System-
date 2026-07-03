from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.services.ml_service import classify_ticket
from app.services.ai_logic import generate_resolution


def detect_priority(title: str, description: str):
    text = f"{title} {description}".lower()

    high_words = [
        "charged twice",
        "duplicate payment",
        "crash",
        "cannot login",
        "refund",
        "payment failed",
    ]

    medium_words = [
        "delay",
        "shipping",
        "password",
        "tracking",
    ]

    if any(word in text for word in high_words):
        return "high"

    if any(word in text for word in medium_words):
        return "medium"

    return "low"


def create_ticket(
    db: Session,
    title: str,
    description: str,
    customer_contact: str = "website customer",
):
    category = classify_ticket(title, description)

    ai_suggested_resolution = generate_resolution(
        category,
        title,
        description,
    )

    priority = detect_priority(title, description)

    ticket = Ticket(
        title=title,
        description=description,
        customer_contact=customer_contact,
        support_inbox="ddwer5777@gmail.com",
        category=category,
        priority=priority,
        status="open",
        ai_suggested_resolution=ai_suggested_resolution,
        resolution=None,
        agent_response=None,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def get_all_tickets(db: Session):
    return db.query(Ticket).all()


def resolve_ticket(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        return None

    ticket.status = "resolved"

    ticket.resolution = (
        ticket.ai_suggested_resolution
        or "Resolved by support agent."
    )

    db.commit()
    db.refresh(ticket)

    return ticket


def respond_to_ticket(
    db: Session,
    ticket_id: int,
    response: str,
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        return None

    ticket.agent_response = response
    ticket.resolution = response
    ticket.status = "resolved"

    db.commit()
    db.refresh(ticket)

    return ticket
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import ticket_service
from app.models.ticket import Ticket
from app.services.search_service import search_tickets
from app.services.ai_response_service import generate_response
from app.services.embedding_service import search_by_embedding
from app.services.agent_service import ticket_agent
from app.services.analytics_service import get_system_stats
from app.services.sla_service import predict_sla_risk
from app.services.bulk_processor import process_all_tickets

router = APIRouter(prefix="/tickets", tags=["Tickets"])

SUPPORT_INBOX = "ddwer5777@gmail.com"


class TicketResponseRequest(BaseModel):
    response: str


@router.post("/create")
def create_ticket(
    title: str,
    description: str,
    customer_contact: str = "website customer",
    db: Session = Depends(get_db),
):
    ticket = ticket_service.create_ticket(
        db=db,
        title=title,
        description=description,
        customer_contact=customer_contact,
    )

    return {
        "message": "Ticket created and sent to support inbox",
        "ticket_id": ticket.id,
        "support_inbox": ticket.support_inbox,
        "customer_contact": ticket.customer_contact,
    }


@router.get("/")
def get_tickets(db: Session = Depends(get_db)):
    return ticket_service.get_all_tickets(db)


@router.put("/{ticket_id}/resolve")
def resolve_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = ticket_service.resolve_ticket(db, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {
        "message": "Ticket resolved",
        "ticket_id": ticket.id,
        "status": ticket.status,
        "resolution": ticket.resolution,
    }


@router.put("/{ticket_id}/respond")
def respond_to_ticket(
    ticket_id: int,
    payload: TicketResponseRequest,
    db: Session = Depends(get_db),
):
    ticket = ticket_service.respond_to_ticket(
        db=db,
        ticket_id=ticket_id,
        response=payload.response,
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return {
        "message": "Support response sent successfully.",
        "ticket_id": ticket.id,
        "status": ticket.status,
        "customer_contact": ticket.customer_contact,
        "support_inbox": ticket.support_inbox,
        "response": ticket.agent_response,
    }
@router.post("/seed-demo")
def seed_demo_tickets(db: Session = Depends(get_db)):
    demo_tickets = [
        {
            "title": "Duplicate payment after checkout",
            "description": "Customer says they were charged twice after completing checkout with their debit card.",
            "customer_contact": "customer1@example.com",
        },
        {
            "title": "Refund delay for canceled order",
            "description": "Customer canceled an order five days ago but still has not received their refund.",
            "customer_contact": "customer2@example.com",
        },
        {
            "title": "Login fails after password reset",
            "description": "Customer reset their password successfully but still cannot log into the account.",
            "customer_contact": "customer3@example.com",
        },
        {
            "title": "Package tracking not updating",
            "description": "Customer says their package tracking has not changed for four days.",
            "customer_contact": "customer4@example.com",
        },
        {
            "title": "Mobile app crashes on order history",
            "description": "Customer reports the mobile app crashes every time they open the order history page.",
            "customer_contact": "customer5@example.com",
        },
        {
            "title": "Card payment approved but order failed",
            "description": "Customer says the bank approved the payment but the order did not appear in their account.",
            "customer_contact": "customer6@example.com",
        },
    ]

    created = []

    for item in demo_tickets:
        ticket = ticket_service.create_ticket(
            db=db,
            title=item["title"],
            description=item["description"],
            customer_contact=item["customer_contact"],
        )

        created.append(ticket.id)

    return {
        "message": "Demo tickets created and sent to support inbox",
        "support_inbox": SUPPORT_INBOX,
        "created_ticket_ids": created,
    }


@router.get("/search")
def search(query: str, db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db)
    results = search_tickets(query, tickets)

    return [_ticket_response(t, score) for t, score in results]


@router.get("/search-ai")
def search_ai(query: str, db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db)
    results = search_by_embedding(query, tickets)

    return [_ticket_response(t, score) for t, score in results]


@router.get("/ai-help")
def ai_help(query: str, db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db)
    results = search_by_embedding(query, tickets)

    global_questions = [
        "summarize",
        "summary",
        "overview",
        "risk",
        "biggest",
        "prioritize",
        "priority",
        "complaining",
        "complaints",
        "all tickets",
    ]

    if not results and any(word in query.lower() for word in global_questions):
        results = [(ticket, 1.0) for ticket in tickets]

    return generate_response(query, results)


@router.get("/agent")
def agent(query: str):
    return ticket_agent(query)


@router.get("/stats")
def stats():
    return get_system_stats()


@router.get("/sla")
def sla(ticket_id: int, db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db)

    ticket = next(
        (t for t in tickets if t.id == ticket_id),
        None,
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return predict_sla_risk(ticket)


@router.post("/bulk-process")
def bulk(db: Session = Depends(get_db)):
    tickets = ticket_service.get_all_tickets(db)
    return process_all_tickets(tickets)


def _ticket_response(ticket: Ticket, score: float = 1.0):
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "customer_contact": ticket.customer_contact,
        "support_inbox": ticket.support_inbox,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
        "resolution": ticket.resolution,
        "agent_response": ticket.agent_response,
        "ai_suggested_resolution": ticket.ai_suggested_resolution,
        "created_at": ticket.created_at,
        "score": float(score),
    }
from app.services.agent_service import ticket_agent


def process_all_tickets(tickets):
    """
    Simulates AI support team handling all tickets
    """

    results = []

    for t in tickets:
        result = ticket_agent(t.title + " " + t.description)
        results.append({
            "ticket_id": t.id,
            "action": result["action_taken"],
            "status": result["ticket"]["status"],
            "priority": result["ticket"]["priority"]
        })

    return results
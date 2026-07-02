def apply_action(ticket, action: str):
    """
    Simulated autonomous system actions
    """

    if action == "auto_resolve":
        ticket.status = "resolved"
        ticket.priority = "low"
        ticket.resolution = "Auto-resolved using similar past tickets."

    elif action == "suggest_resolution":
        ticket.status = "in_progress"
        ticket.priority = "medium"

    elif action == "escalate":
        ticket.status = "escalated"
        ticket.priority = "high"

    return ticket
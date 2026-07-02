def predict_sla_risk(ticket):
    """
    Simple heuristic SLA risk model
    """

    risk = 0.0

    if ticket.priority == "high":
        risk += 0.5

    if ticket.status == "open":
        risk += 0.3

    if "error" in ticket.description.lower():
        risk += 0.2

    if risk > 1:
        risk = 1.0

    return {
        "ticket_id": ticket.id,
        "sla_risk_score": round(risk, 2),
        "risk_level": "high" if risk > 0.7 else "medium" if risk > 0.4 else "low"
    }
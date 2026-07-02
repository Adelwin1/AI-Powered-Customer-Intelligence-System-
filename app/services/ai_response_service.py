from collections import Counter


def generate_response(query: str, results):
    if not results:
        return {
            "answer": """
I could not find a strong match in your current tickets.

Try asking me something like:
- What are customers complaining about?
- Which ticket should we fix first?
- What is the biggest risk right now?
- Summarize the billing issues.
- Which tickets look similar?
""".strip(),
            "confidence": 0.0,
            "mode": "free-local-ai",
        }

    query_lower = query.lower()
    matched_tickets = [ticket for ticket, score in results[:6]]
    top_ticket, top_score = results[0]

    categories = Counter([(t.category or "uncategorized").lower() for t in matched_tickets])
    priorities = Counter([(getattr(t, "priority", None) or "low").lower() for t in matched_tickets])
    statuses = Counter([(getattr(t, "status", None) or "open").lower() for t in matched_tickets])

    total = len(matched_tickets)
    open_count = statuses.get("open", 0)
    resolved_count = statuses.get("resolved", 0)
    high_count = priorities.get("high", 0)
    medium_count = priorities.get("medium", 0)
    low_count = priorities.get("low", 0)

    top_category = categories.most_common(1)[0][0]
    top_priority = priorities.most_common(1)[0][0]

    risk_score = min(100, (open_count * 20) + (high_count * 30) + (medium_count * 15))
    risk_level = "low"

    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 35:
        risk_level = "medium"

    repeated_issue = _detect_repeated_issue(matched_tickets)
    recommended_actions = _recommended_actions(top_category, top_priority, open_count)
    ticket_lines = _format_ticket_lines(matched_tickets)

    intro = _build_intro(
        query_lower=query_lower,
        top_category=top_category,
        top_ticket=top_ticket,
        risk_level=risk_level,
        risk_score=risk_score,
    )

    answer = f"""
{intro}

Here is what I found:

• I reviewed {total} related ticket{'' if total == 1 else 's'}.
• {open_count} are still open.
• {resolved_count} are resolved.
• {high_count} are high priority.
• The strongest category is {top_category}.
• The strongest match is Ticket #{top_ticket.id}: "{top_ticket.title}".

Pattern I am seeing:
{repeated_issue}

My read:
{_risk_explanation(top_category, risk_level)}

What I would do next:
{recommended_actions}

Related tickets:
{ticket_lines}

Confidence: {float(top_score):.2f}
Mode: Free local AI
""".strip()

    return {
        "answer": answer,
        "top_match": {
            "id": top_ticket.id,
            "title": top_ticket.title,
            "description": top_ticket.description,
            "category": top_ticket.category,
            "priority": getattr(top_ticket, "priority", "low"),
            "status": getattr(top_ticket, "status", "open"),
        },
        "confidence": float(top_score),
        "mode": "free-local-ai",
    }


def _build_intro(query_lower: str, top_category: str, top_ticket, risk_level: str, risk_score: int):
    if _is_priority_query(query_lower):
        return (
            f"I would start with the {top_category} tickets. "
            f"The strongest one is Ticket #{top_ticket.id}, and the current risk looks {risk_level} "
            f"with a score of {risk_score}/100."
        )

    if _is_complaint_query(query_lower):
        return (
            f"Customers seem to be complaining mostly about {top_category}. "
            f"The clearest example is Ticket #{top_ticket.id}: \"{top_ticket.title}\"."
        )

    if _is_risk_query(query_lower):
        return (
            f"The biggest visible risk right now is {top_category}. "
            f"I would treat it as {risk_level} risk based on the matching tickets."
        )

    if _is_summary_query(query_lower):
        return (
            f"Here is the quick support summary: most of the related activity points to {top_category}, "
            f"with {risk_score}/100 operational risk."
        )

    return (
        f"Good question. Based on the tickets I found, this connects most strongly to {top_category}. "
        f"The best match is Ticket #{top_ticket.id}: \"{top_ticket.title}\"."
    )


def _format_ticket_lines(tickets):
    return "\n".join(
        [
            f"- Ticket #{t.id}: {t.title} | {t.category or 'uncategorized'} | "
            f"{getattr(t, 'priority', 'low')} | {getattr(t, 'status', 'open')}"
            for t in tickets
        ]
    )


def _is_priority_query(query: str):
    return any(word in query for word in ["prioritize", "priority", "first", "urgent", "work on", "fix first"])


def _is_complaint_query(query: str):
    return any(word in query for word in ["complain", "complaint", "complaining", "problem", "issue"])


def _is_risk_query(query: str):
    return any(word in query for word in ["risk", "danger", "biggest", "critical", "breach"])


def _is_summary_query(query: str):
    return any(word in query for word in ["summary", "summarize", "overview", "recap"])


def _detect_repeated_issue(tickets):
    text = " ".join([f"{t.title} {t.description}" for t in tickets]).lower()

    patterns = {
        "duplicate charges or failed payments": ["charged twice", "duplicate", "payment failed", "card", "checkout"],
        "refund delays": ["refund", "waiting", "delay", "canceled"],
        "login or account access problems": ["login", "password", "reset", "account"],
        "shipping and tracking delays": ["shipping", "tracking", "package", "delivery"],
        "technical stability problems": ["crash", "bug", "error", "broken", "loading"],
    }

    scores = {pattern: sum(1 for keyword in keywords if keyword in text) for pattern, keywords in patterns.items()}
    best_pattern = max(scores, key=scores.get)

    if scores[best_pattern] == 0:
        return "The tickets are related, but I do not see enough repeated wording yet to call a clear root cause."

    return f"The strongest repeated pattern is {best_pattern}."


def _recommended_actions(category: str, priority: str, open_count: int):
    category = (category or "").lower()
    priority = (priority or "").lower()

    if category in ["billing", "payment"]:
        actions = [
            "1. Check payment logs for duplicate charges or failed checkout events.",
            "2. Compare refund-related tickets and see if they share the same payment flow.",
            "3. Prepare one clear support response for affected customers.",
        ]
    elif category in ["authentication", "login"]:
        actions = [
            "1. Review password reset and account lockout behavior.",
            "2. Check whether customers are failing at the same login step.",
            "3. Escalate repeated login failures to engineering.",
        ]
    elif category in ["shipping", "delivery"]:
        actions = [
            "1. Review tracking events and carrier delays.",
            "2. Find packages with stale tracking updates.",
            "3. Proactively update customers before they send more tickets.",
        ]
    else:
        actions = [
            "1. Review the top matching tickets manually.",
            "2. Group similar issues by category and priority.",
            "3. Escalate repeated unresolved issues.",
        ]

    if priority == "high" or open_count >= 3:
        actions.append("4. Escalate this because the priority or open-ticket volume is elevated.")

    return "\n".join(actions)


def _risk_explanation(category: str, risk_level: str):
    category = (category or "uncategorized").lower()

    if category in ["billing", "payment"]:
        return "Billing problems matter because they can quickly damage trust, create refund pressure, and affect revenue confidence."
    if category in ["authentication", "login"]:
        return "Login problems matter because customers are blocked from using the product at all."
    if category in ["shipping", "delivery"]:
        return "Shipping problems matter because customers often follow up repeatedly when tracking is unclear."
    if risk_level == "high":
        return "The open-ticket count and priority mix suggest this should be handled quickly."

    return "The signal is worth watching, but it does not look severe yet."
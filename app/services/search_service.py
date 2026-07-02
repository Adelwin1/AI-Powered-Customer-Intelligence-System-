def search_tickets(query: str, tickets):
    query_words = set(query.lower().split())
    results = []

    for ticket in tickets:
        text = f"{ticket.title} {ticket.description} {ticket.category or ''}".lower()
        text_words = set(text.split())

        matches = query_words.intersection(text_words)
        score = len(matches) / max(len(query_words), 1)

        if score > 0:
            results.append((ticket, score))

    results.sort(key=lambda item: item[1], reverse=True)
    return results
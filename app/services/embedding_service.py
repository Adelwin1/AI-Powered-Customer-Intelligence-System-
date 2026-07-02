from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

vectorizer = TfidfVectorizer(stop_words="english")


def embed_text(text: str):
    return text


def search_by_embedding(query: str, tickets):
    corpus = [
        f"{t.title} {t.description} {t.category or ''} {getattr(t, 'priority', '')} {getattr(t, 'status', '')}"
        for t in tickets
    ]

    if len(corpus) == 0:
        return []

    X = vectorizer.fit_transform(corpus + [query])

    query_vec = X[-1]
    docs_vec = X[:-1]

    scores = cosine_similarity(query_vec, docs_vec)[0]

    results = [
        (ticket, score)
        for ticket, score in zip(tickets, scores)
        if score >= 0.08
    ]

    results.sort(key=lambda x: x[1], reverse=True)

    return results
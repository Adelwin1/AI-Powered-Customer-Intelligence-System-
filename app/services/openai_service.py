from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


# -------------------------
# EMBEDDINGS
# -------------------------
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


# -------------------------
# CHAT / RESPONSE GENERATION
# -------------------------
def generate_answer(context: str, question: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful customer support assistant."
            },
            {
                "role": "user",
                "content": f"""
Context from past tickets:
{context}

User question:
{question}

Give a helpful support response.
"""
            }
        ]
    )

    return response.choices[0].message.content
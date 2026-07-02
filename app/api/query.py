from fastapi import APIRouter
from app.services.rag_service import ask_question

router = APIRouter(prefix="/query", tags=["AI"])

@router.get("/")
def query(question: str):
    return {
        "question": question,
        "answer": ask_question(question)
    }
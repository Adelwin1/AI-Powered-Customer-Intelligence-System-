from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.models import user, ticket
from app.api import auth, tickets, dashboard, query


app = FastAPI(
    title="AI Customer Intelligence System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ai-customer-intelligence-dashboard-flame.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(dashboard.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"message": "AI Customer Intelligence System is running"}
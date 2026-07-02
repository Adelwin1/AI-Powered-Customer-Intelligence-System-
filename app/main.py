from fastapi import FastAPI

from app.core.database import Base, engine
from app.models import user, ticket  # ensures models register

from app.api import auth, tickets, dashboard
from app.api import auth, tickets, dashboard, query

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="AI Customer Intelligence System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# create tables
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(dashboard.router) 
app.include_router(query.router)

@app.get("/")
def root():
    return {"message": "AI Customer Intelligence System is running"}
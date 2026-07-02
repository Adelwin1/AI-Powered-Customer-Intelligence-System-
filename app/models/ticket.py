from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    customer_contact = Column(String, default="website customer")
    support_inbox = Column(String, default="ddwer5777@gmail.com")

    category = Column(String, nullable=True)
    priority = Column(String, default="low")
    status = Column(String, default="open")

    embedding = Column(Text, nullable=True)

    ai_suggested_resolution = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    agent_response = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
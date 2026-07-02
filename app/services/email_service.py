import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


def send_support_email(ticket):
    subject = f"New Support Ticket #{ticket.id}"

    body = f"""
A new customer support ticket has been created.

Ticket ID: {ticket.id}

Title:
{ticket.title}

Description:
{ticket.description}

Category:
{ticket.category}

Priority:
{ticket.priority}

Customer:
{ticket.customer_contact}

Please log into the dashboard to respond.
"""

    _send_email(
        to_email=ticket.support_inbox,
        subject=subject,
        body=body,
    )


def send_customer_email(ticket):
    if (
        not ticket.customer_contact
        or "@" not in ticket.customer_contact
    ):
        return

    subject = f"Update on your Support Ticket #{ticket.id}"

    body = f"""
Hello,

Our support team has responded to your ticket.

Ticket:
{ticket.title}

Response:
{ticket.agent_response}

Thank you for contacting support.
"""

    _send_email(
        to_email=ticket.customer_contact,
        subject=subject,
        body=body,
    )


def _send_email(to_email: str, subject: str, body: str):
    message = MIMEMultipart()

    message["From"] = settings.GMAIL_ADDRESS
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()

        smtp.login(
            settings.GMAIL_ADDRESS,
            settings.GMAIL_APP_PASSWORD,
        )

        smtp.sendmail(
            settings.GMAIL_ADDRESS,
            to_email,
            message.as_string(),
        )
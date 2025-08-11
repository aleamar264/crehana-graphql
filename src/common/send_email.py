from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr
from models.models import Tasks
from utils.fastapi.email.email_sender import fm


async def send_email_for_task(user: EmailStr, task: Tasks)-> None:
    email_message = MessageSchema(
        subject="Welcome Email to Datahub",
        recipients=[user],
        body=f"You have assigned the task {task.id}",
        subtype=MessageType.html,
    )
    fm.config.SUPPRESS_SEND = 1
    await fm.send_message(message=email_message)
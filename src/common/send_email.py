from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr

from models.models import Tasks
from utils.fastapi.email.email_sender import fm


async def send_email_for_task(user: EmailStr, task: Tasks) -> None:
	"""
	Asynchronously sends an email notification to a user about a task assignment.

	Args:
		user (EmailStr): The email address of the recipient.
		task (Tasks): The task object containing assignment details.

	Returns:
		None

	Raises:
		Any exceptions raised by the underlying email sending library.

	Note:
		The email sending is suppressed (fm.config.SUPPRESS_SEND = 1), so no actual email will be sent.
	"""
	email_message = MessageSchema(
		subject="Welcome Email to Datahub",
		recipients=[user],
		body=f"You have assigned the task {task.id}",
		subtype=MessageType.html,
	)
	fm.config.SUPPRESS_SEND = 1
	await fm.send_message(message=email_message)

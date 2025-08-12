from datetime import UTC, datetime

import pytest

from common.send_email import fm, send_email_for_task
from models.models import Tasks
from schema.tasks import Priority, Status


@pytest.mark.asyncio
async def test_send_email_task():
	"""Test send email"""
	fm.config.SUPPRESS_SEND = 1
	with fm.record_messages() as outbox:
		await send_email_for_task(
			user="user@example.com",
			task=Tasks(
				**{
					"id": "f5ce4021-078d-4fe1-be6b-436162bda768",
					"status": Status.NEW,
					"priority": Priority.LOW,
					"user": "c54a9f74-2a33-47fe-b40c-9d860e7c6f73",
					"created_at": datetime.now(UTC),
					"title": "Test task",
					"description": "Test description",
					"task_list_id": None,
				}
			),
		)

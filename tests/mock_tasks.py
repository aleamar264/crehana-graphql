from datetime import UTC, datetime
from uuid import UUID

from schema.tasks import Priority, Status

TASK_DATA_MOCK = [
	{
		"id": UUID("6aa51c81-b757-4baa-928a-afa23b97e7a5"),
		"status": Status.NEW,
		"priority": Priority.CRITICAL,
		"user": UUID("450125d3-960c-4e47-ba62-12a96cec9ba5"),
		"created_at": datetime.now(UTC),
		"updated_at": None,
		"task_list_id": None,
		"title": "Test",
		"description": "Description test",
	},
	{
		"id": UUID("6aa51c81-b757-4baa-928a-afa23b97e7a8"),
		"status": Status.BLOCKED,
		"priority": Priority.HIGH,
		"user": UUID("123e4567-e89b-12d3-a456-426614174000"),
		"created_at": datetime.now(UTC),
		"updated_at": None,
		"task_list_id": None,
		"title": "Another Test",
		"description": "Description test",
	},
]

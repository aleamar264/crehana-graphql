from datetime import UTC, datetime
from uuid import UUID

from models.models import Tasks
from schema.tasks import Priority, Status

MOCK_TASK_LIST = {
	"id": UUID("fbaa20cf-91aa-49db-bae9-105bc052421c"),
	"name": "Test list",
	"created_at": datetime.now(UTC),
	"updated_at": None,
	"tasks": [],
}

MOCK_TASK_LIST_WITH_TASKS = {
	"id": UUID("fbaa20cf-91aa-49db-bae9-105bc052421c"),
	"name": "Test list",
	"created_at": datetime.now(UTC),
	"updated_at": None,
	"tasks": [
		Tasks(
			**{
				"id": UUID("6aa51c81-b757-4baa-928a-afa23b97e7a8"),
				"status": Status.BLOCKED,
				"priority": Priority.HIGH,
				"user": UUID("123e4567-e89b-12d3-a456-426614174000"),
				"created_at": datetime.now(UTC),
				"updated_at": None,
				"task_list_id": None,
				"title": "Another Test",
				"description": "Description test",
			}
		)
	],
}

MOCK_TASK_LIST_WITH_TASKS_ID = {
	"id": UUID("fbaa20cf-91aa-49db-bae9-105bc052421c"),
	"name": "Test list",
	"created_at": datetime.now(UTC),
	"updated_at": None,
	"tasks": [
		UUID("6aa51c81-b757-4baa-928a-afa23b97e7a8"),
	],
}

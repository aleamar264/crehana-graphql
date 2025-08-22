from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

import strawberry

from schema.tasks import ListTaskGQL, TaskGQLResponse, Tasks, TaskUpdates


@strawberry.enum
class PriorityGQLEnum(Enum):
	CRITICAL = 1
	HIGH = 2
	MEDIUM = 3
	LOW = 4
	OPTIONAL = 5


@strawberry.enum
class StatusGQLEnum(Enum):
	NEW = "new"
	ACTIVE = "active"
	COMPLETED = "completed"
	BLOCKED = "blocked"
	ERROR = "error"


@strawberry.experimental.pydantic.type(model=TaskGQLResponse)
class TasksType:
	status: StatusGQLEnum = strawberry.field(default=StatusGQLEnum.NEW)
	priority: PriorityGQLEnum = strawberry.field(default=PriorityGQLEnum.LOW)
	user: UUID | None
	title: str
	description: str
	created_at: datetime
	updated_at: datetime | None
	id: UUID
	task_list_id: UUID | None = None


@strawberry.experimental.pydantic.type(model=ListTaskGQL)
class ListTaskType:
	tasks: list[TasksType] = strawberry.field(default_factory=[])
	name: str = strawberry.field()
	created_at: datetime
	updated_at: datetime | None
	id: UUID


# =================================== Input ===========================================


@strawberry.experimental.pydantic.input(model=Tasks)
class TasksInput:
	status: StatusGQLEnum = strawberry.field(default=StatusGQLEnum.NEW)
	priority: PriorityGQLEnum = strawberry.field(default=PriorityGQLEnum.LOW)
	user: UUID | None
	title: str
	description: str
	created_at: datetime | None = strawberry.field(
		default_factory=lambda: datetime.now(UTC)
	)
	updated_at: datetime | None
	task_list_id: UUID | None = None


@strawberry.input()
class ListTaskInput:
	tasks: list[UUID] = strawberry.field(default_factory=[])
	name: str = strawberry.field()
	created_at: datetime | None = strawberry.field(
		default_factory=lambda: datetime.now(UTC)
	)
	updated_at: datetime | None = None


# ======================= Update ==========================


@strawberry.input
class DateTime:
	updated_at: datetime = strawberry.field(default=datetime.now())


@strawberry.input
class ListTasksUpdate(DateTime):
	tasks: list[UUID] | None = None
	name: str | None = None


@strawberry.experimental.pydantic.input(model=TaskUpdates)
class TasksUpdateGQL:
	status: StatusGQLEnum | None = strawberry.field(default=StatusGQLEnum.NEW)
	priority: PriorityGQLEnum | None = strawberry.field(default=PriorityGQLEnum.LOW)
	user: UUID | None = None
	title: str | None = None
	description: str | None = None
	task_list_id: UUID | None = None
	updated_at: datetime | None = strawberry.field(
		default_factory=lambda: datetime.now(UTC)
	)
	created_at: datetime | None = None

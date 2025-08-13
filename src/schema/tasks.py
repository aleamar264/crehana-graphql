from datetime import UTC, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Status(Enum):
	NEW = "new"
	ACTIVE = "active"
	COMPLETED = "completed"
	BLOCKED = "blocked"
	ERROR = "error"


class Priority(Enum):
	CRITICAL = 1
	HIGH = 2
	MEDIUM = 3
	LOW = 4
	OPTIONAL = 5


class UpdatedCreated(BaseModel):
	created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
	updated_at: datetime | None = Field(None)


class Tasks(UpdatedCreated):
	status: Status = Field(Status.NEW, description="Status of one task")
	priority: Priority = Field(Priority.LOW, description="Priority for a task")
	user: UUID | None = Field(None, description="User in charge of the task")
	title: str = Field(..., max_length=25, min_length=3)
	description: str = Field(..., max_length=255)
	task_list_id: UUID | None = None


class ListTask(UpdatedCreated):
	tasks: list[Tasks] = Field(default=[])
	name: str = Field(
		pattern=r" [a-zA-Z0-9]", description="Name of the list", default=""
	)


class TasksResponse(Tasks):
	id: UUID = Field(..., description="Id of the tasks")
	model_config = ConfigDict(from_attributes=True)



class ListTasksResponse(ListTask):
	id: UUID = Field(..., description="Id of the tasks")
	model_config = ConfigDict(from_attributes=True)


class GQL(BaseModel):
	model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class TasksGQL(Tasks, GQL): ...

class ListTaskGQLCreation(GQL, UpdatedCreated):
	tasks: list[TasksResponse] = Field(default=[])
	name: str = Field(
		pattern=r" [a-zA-Z0-9]", description="Name of the list", default=""
	)

class ListTaskGQL(ListTask, GQL): ...


class TaskGQLResponse(TasksGQL):
	id: UUID


class ListTaskGQLResponse(ListTaskGQL):
	id: UUID


class TaskUpdates(BaseModel):
	status: Status = Field(Status.NEW, description="Status of one task")
	priority: Priority = Field(Priority.LOW, description="Priority for a task")
	user: UUID | None = Field(None, description="User in charge of the task")
	title: str | None = None
	description: str | None = None
	task_list_id: UUID | None = None
	created_at: datetime | None = None
	updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

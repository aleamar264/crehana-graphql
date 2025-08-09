from enum import Enum
from typing import Annotated, Any
from uuid import UUID

import strawberry
from fastapi import Depends
from strawberry.types import Info

from models.models import TaskList, Tasks
from schema.grapql_schemas import ListTasksUpdate, TasksUpdateGQL
from schema.tasks import ListTaskGQLResponse, TaskGQLResponse, TaskUpdates
from .tasks import tasks_repository, tasks_list_repository

from schema.grapql_schemas import TasksType, ListTaskType


def convert_enum(value: Any) -> Any:
	if isinstance(value, Enum):
		return value.value  # Convert Enum to its value
	return value


@strawberry.type
class UpdateMutation:
	"""Class that update the data from the employee using GraphQL"""

	@strawberry.mutation
	async def update_tasks(
		self, id: Annotated[str, UUID], tasks: TasksUpdateGQL, info: Info
	) -> TasksType:
		_entity = strawberry.asdict(tasks)
		# _entity = {k: v for k, v in _entity.items() if v is not None}
		converted_data = {key: convert_enum(value) for key, value in _entity.items()}
		result = await tasks_repository.update_entity(
			db=info.context.db,
			entity_schema=TaskUpdates(
				**converted_data, **{"created_at": None}
			).model_dump(exclude_none=True),
			filter=(),  # type: ignore
			entity_id=id,
		)
		__tasks = TasksType.from_pydantic(TaskGQLResponse.model_validate(result))
		__tasks = strawberry.asdict(__tasks)  # type: ignore
		return TasksType(**__tasks)  # type: ignore

	@strawberry.mutation
	async def list_tasks_update(
		self, id: Annotated[str, UUID], list_tasks: ListTasksUpdate, info: Info
	) -> ListTaskType:
		entity = strawberry.asdict(list_tasks)
		_entity = {k: v for k, v in entity.items() if v is not None}
		converted_data = {key: convert_enum(value) for key, value in _entity.items()}
		session = info.context.db
		result = await tasks_list_repository.update_entity(
			entity_id=id,
			db=session,
			entity_schema=converted_data,
			filter=(),  # type: ignore
		)

		await session.refresh(result, attribute_names=["tasks"])
		__tasks_list = ListTaskType.from_pydantic(
			ListTaskGQLResponse.model_validate(result)
		)
		__tasks_list = strawberry.asdict(__tasks_list)  # type: ignore
		return ListTaskType(**__tasks_list)  # type: ignore

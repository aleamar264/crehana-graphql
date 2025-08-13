from enum import Enum
from typing import Annotated, Any
from uuid import UUID

import strawberry
from sqlalchemy import select
from strawberry.types import Info

from common.send_email import send_email_for_task
from models.models import TaskList, Tasks
from schema.grapql_schemas import (
	ListTasksUpdate,
	ListTaskType,
	TasksType,
	TasksUpdateGQL,
)
from schema.tasks import ListTaskGQLResponse, TaskGQLResponse, TaskUpdates
from services.users import user_repository

from .tasks import tasks_list_repository, tasks_repository


def convert_enum(value: Any) -> Any:
	if isinstance(value, Enum):
		return value.value  # Convert Enum to its value
	return value


async def update_task_in_task_list(
	tasks_ids: list[Annotated[str, UUID]], id: Annotated[str, UUID], info: Info
) -> None:
	async with info.context.db as session:
		tasks = await session.execute(select(Tasks).where(Tasks.id.in_(tasks_ids)))
		tasks = list(tasks.scalars())

		for task in tasks:
			task.task_list_id = UUID(id)
		await session.commit()


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
			entity_schema=TaskUpdates(**converted_data).model_dump(exclude_none=True),
			filter=(),  # type: ignore
			entity_id=id,
		)
		if (_user := converted_data.get("user")) is not None and _user != str(
			result.user
		):
			user = await user_repository.get_entity_by_id(
				db=info.context.db, entity_id=str(converted_data["user"])
			)
			await send_email_for_task(user=str(user.email), task=result)
		__tasks = TasksType.from_pydantic(TaskGQLResponse.model_validate(result))
		return __tasks

	@strawberry.mutation
	async def list_tasks_update(
		self, id: Annotated[str, UUID], list_tasks: ListTasksUpdate, info: Info
	) -> ListTaskType:
		entity = strawberry.asdict(list_tasks)
		_entity = {k: v for k, v in entity.items() if v is not None}
		converted_data = {key: convert_enum(value) for key, value in _entity.items()}
		if tasks := converted_data.get("tasks", None):
			del converted_data["tasks"]
			await update_task_in_task_list(tasks_ids=tasks, id=id, info=info)
		session = info.context.db
		result: TaskList = await tasks_list_repository.update_entity(
			entity_id=id,
			db=session,
			entity_schema=converted_data,
			filter=(),  # type: ignore
		)

		tasks = []

		await session.refresh(result, attribute_names=["tasks"])
		tasks = [TaskGQLResponse.model_validate(t) for t in result.tasks]
		items_dict = result.__dict__
		items_dict["tasks"] = tasks
		new_items: ListTaskGQLResponse = ListTaskGQLResponse.model_construct(
			**items_dict
		)
		__tasks_list = ListTaskType.from_pydantic(
			ListTaskGQLResponse.model_validate(new_items)
		)
		return __tasks_list

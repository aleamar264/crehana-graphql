import asyncio
from dataclasses import asdict
from enum import Enum
from typing import Any

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from strawberry.types import Info

from common.send_email import send_email_for_task
from schema.grapql_schemas import (
	ListTaskInput,
	ListTaskType,
	TaskGQLResponse,
	TasksInput,
	TasksType,
)
from schema.grapql_schemas import Tasks as TaskSchema
from schema.tasks import ListTask as ListTaskSchema, ListTaskGQLCreation, TasksResponse
from schema.tasks import ListTaskGQLResponse
from services.users import user_repository
from utils.db.crud.entity import GeneralCrudAsync
from utils.exceptions import (
	EntityAlreadyExistsError,
)

from .tasks import tasks_list_repository, tasks_repository


async def get_other_entity(
	column: InstrumentedAttribute,  # type: ignore
	schema_value: int | str,
	db: AsyncSession,
	crud: GeneralCrudAsync,  # type: ignore
	message: str = "Entity already exist",
) -> None:
	"""Auxiliar function that retrieve any entity.

	Args:
		column (InstrumentedAttribute): Column of the SQLAlchemy model
		schema_value (int | str): he value can be an string (UUID/email/etc) or integer
		db (AsyncSession): SQLAlchemy Async Session
		crud (GeneralCrudAsync): Class with the crud that is needed to retrieve the data
		message (str, optional): Message for the raise message. Defaults to "Entity already exist".

	Raises:
		EntityAlreadyExistsError: If the entity already exist raise and error with the message from the arg :variable:`message`
		and code :variable:`Entity already exist`.
	"""
	if await crud.get_entity_by_args(column, schema_value, db, filter=()) is not None:  # type: ignore
		raise EntityAlreadyExistsError(message)


def convert_enum(value: Any) -> Any:
	if isinstance(value, Enum):
		return value.value  # Convert Enum to its value
	return value


async def tasks_lists_mutation(tasks_list: ListTaskInput, info: Info) -> ListTaskType:
	"""
	Asynchronously creates a new tasks list entity in the database and returns the corresponding GraphQL type.

	Args:
		tasks_list (ListTaskInput): The input data for the tasks list to be created.
		info (Info): GraphQL resolver info containing context, including the database session.

	Returns:
		ListTaskType: The created tasks list represented as a GraphQL type.

	Raises:
		ValidationError: If the input data does not conform to the expected schema.
		Exception: For any database or repository errors during entity creation or refresh.
	"""
	session = info.context.db
	entity = strawberry.asdict(tasks_list)
	converted_data = {key: convert_enum(value) for key, value in entity.items()}
	if converted_data["tasks"]:
		tasks = []
		for task in converted_data["tasks"]:
			tasks_ = await tasks_repository.get_entity_by_id(
				db=session, filter=(), entity_id=task
			)
			tasks.append(TasksResponse(**tasks_.__dict__))
		converted_data["tasks"] = tasks
	entity_schema = ListTaskGQLCreation(**converted_data)
	result = await tasks_list_repository.create_entity(
		db=session,
		entity_schema=entity_schema,
	)
	await session.refresh(result, attribute_names=["tasks"])
	tasks = [TaskGQLResponse.model_validate(t) for t in result.tasks]
	items_dict = result.__dict__
	items_dict["tasks"] = tasks

	return ListTaskType.from_pydantic(
		ListTaskGQLResponse.model_construct(**items_dict)
	)


async def tasks_mutation(tasks: TasksInput, info: Info) -> TasksType:
	"""
	Asynchronously creates a new task entity in the database and sends an email notification if the user associated with the task has changed.

	Args:
		tasks (TasksInput): The input data for the task to be created.
		info (Info): The GraphQL resolver info containing context and database session.

	Returns:
		TasksType: The created task entity as a GraphQL type.

	Side Effects:
		- Sends an email notification to the user if the user associated with the task is different from the one in the result.

	Raises:
		ValidationError: If the input data does not conform to the TaskSchema.
		Exception: Propagates exceptions from the repository or email sending functions.
	"""
	entity = strawberry.asdict(tasks)
	converted_data = {key: convert_enum(value) for key, value in entity.items()}
	entity_schema = TaskSchema(**converted_data)
	session = info.context.db
	result = await tasks_repository.create_entity(
		db=session,
		entity_schema=entity_schema,
	)
	if (_user := converted_data.get("user")) is not None and _user != str(result.user):
		user = await user_repository.get_entity_by_id(
			db=info.context.db, entity_id=str(converted_data["user"])
		)
		await send_email_for_task(user=str(user.email), task=result)
	return TasksType.from_pydantic(TaskGQLResponse.model_validate(result))


@strawberry.type
class CreateMutation:
	@strawberry.mutation
	async def create_tasks(self, tasks: TasksInput, info: Info) -> TasksType:
		return await tasks_mutation(tasks=tasks, info=info)

	@strawberry.mutation
	async def create_tasks_lists(
		self, tasks_list: ListTaskInput, info: Info
	) -> ListTaskType:
		return await tasks_lists_mutation(tasks_list=tasks_list, info=info)

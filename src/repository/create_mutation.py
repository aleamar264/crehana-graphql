from dataclasses import asdict
from enum import Enum
from typing import Any

import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from strawberry.types import Info

from common.send_email import send_email_for_task
from schema.tasks import ListTask as ListTaskSchema
from schema.grapql_schemas import (
	ListTaskInput,
	ListTaskType,
	TaskGQLResponse,
	TasksInput,
	TasksType,
)
from schema.grapql_schemas import Tasks as TaskSchema
from schema.tasks import ListTaskGQLResponse
from utils.db.crud.entity import GeneralCrudAsync
from utils.exceptions import (
	EntityAlreadyExistsError,
)

from services.users import user_repository

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
		raise EntityAlreadyExistsError(message, code="ENTITY_IN_DB")


def convert_enum(value: Any) -> Any:
	if isinstance(value, Enum):
		return value.value  # Convert Enum to its value
	return value


@strawberry.type
class CreateMutation:
	@strawberry.mutation
	async def tasks(self, tasks: TasksInput, info: Info) -> TasksType:
		entity = strawberry.asdict(tasks)
		converted_data = {key: convert_enum(value) for key, value in entity.items()}
		entity_schema = TaskSchema(**converted_data)
		session = info.context.db
		result = await tasks_repository.create_entity(
			db=session,
			entity_schema=entity_schema,
		)
		if converted_data.get("user") is not None:
			user = await user_repository.get_entity_by_id(db=info.context.db, entity_id=converted_data["user"])
			await send_email_for_task(user=str(user.email), task=result)
		__tasks = TasksType.from_pydantic(TaskGQLResponse.model_validate(result))
		__tasks = asdict(__tasks)  # type: ignore
		return TasksType(**__tasks)  # type: ignore

	@strawberry.mutation
	async def tasks_lists(self, tasks_list: ListTaskInput, info: Info) -> ListTaskType:
		entity = strawberry.asdict(tasks_list)
		converted_data = {key: convert_enum(value) for key, value in entity.items()}
		entity_schema = ListTaskSchema(**converted_data)
		session = info.context.db
		result = await tasks_list_repository.create_entity(
			db=session,
			entity_schema=entity_schema,
		)
		await session.refresh(result, attribute_names=["tasks"])
		__tasks_list = ListTaskType.from_pydantic(
			ListTaskGQLResponse.model_validate(result)
		)
		__tasks_list = asdict(__tasks_list)  # type: ignore
		return ListTaskType(**__tasks_list)  # type: ignore

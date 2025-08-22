from typing import Annotated
from uuid import UUID

import strawberry
from strawberry.types import Info

from .tasks import tasks_list_repository, tasks_repository


async def delete_task(id: Annotated[str, UUID], info: Info) -> None:
	"""Asynchronously delete a tasks entity in the database.

	Args:
		id (Annotated[str, UUID]): The id of the task to be deleted.
		info (Info): GraphQL resolver info containing context, including the database session.

	Returns:
		None

	Raises:
		ValidationError: If the input data does not conform to the expected schema.
		Exception: For any database or repository errors during entity creation or refresh.
	"""
	await tasks_repository.delete_entity(
		id,
		db=info.context.db,
		filter=(),  # type: ignore
	)


async def delete_task_list(id: Annotated[str, UUID], info: Info) -> None:
	"""Asynchronously delete a tasks list entity in the database.

	Args:
		id (Annotated[str, UUID]): The id of the task to be deleted.
		info (Info): GraphQL resolver info containing context, including the database session.

	Returns:
		None

	Raises:
		ValidationError: If the input data does not conform to the expected schema.
		Exception: For any database or repository errors during entity creation or refresh.
	"""
	session = info.context.db
	task_list = await tasks_list_repository.get_entity_by_id(entity_id=id, db=session)
	if task_list.tasks:
		await session.refresh(task_list, attribute_name=["tasks"])
		[
			await tasks_repository.update_entity(
				entity_id=task.id,
				db=session,
				entity_schema={"task_list_id": None},
			)
			for task in task_list.tasks
		]
	await tasks_list_repository.delete_entity(
		filter=(),  # type: ignore
		entity_id=id,
		db=session,
	)


@strawberry.type
class DeleteMutation:
	@strawberry.mutation
	async def delete_task_mutation(self, id: Annotated[str, UUID], info: Info) -> None:
		await delete_task(id=id, info=info)

	@strawberry.mutation
	async def delete_task_list_mutation(self, id: Annotated[str, UUID], info: Info) -> None:
		await delete_task_list(id=id, info=info)

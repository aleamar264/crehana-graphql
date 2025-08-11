from typing import Annotated
from uuid import UUID

import strawberry
from strawberry.types import Info

from .tasks import tasks_list_repository, tasks_repository


@strawberry.type
class DeleteMutation:
	@strawberry.mutation
	async def delete_task(self, id: Annotated[str, UUID], info: Info) -> None:
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

	@strawberry.mutation
	async def delete_task_list(self, id: Annotated[str, UUID], info: Info) -> None:
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
		await tasks_list_repository.delete_entity(
			filter=(),  # type: ignore
			entity_id=id,
			db=info.context.db,
		)

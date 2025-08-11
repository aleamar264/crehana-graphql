from typing import Annotated
from uuid import UUID

import strawberry
from strawberry.types import Info

from .tasks import tasks_list_repository, tasks_repository


@strawberry.type
class DeleteMutation:
	@strawberry.mutation
	async def delete_task(self, id: Annotated[str, UUID], info: Info) -> None:
		await tasks_repository.delete_entity(
			id,
			db=info.context.db,
			filter=(),  # type: ignore
		)

	@strawberry.mutation
	async def delete_task_list(self, id: Annotated[str, UUID], info: Info) -> None:
		await tasks_list_repository.delete_entity(
			filter=(),  # type: ignore
			entity_id=id,
			db=info.context.db,
		)

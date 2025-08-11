from typing import Any

import sqlalchemy as sa
import strawberry
from pydantic import BaseModel
from sqlalchemy import lambda_stmt
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base
from models.models import TaskList, Tasks
from schema.grapql_schemas import ListTaskType, TasksType
from schema.tasks import (
	ListTaskGQLResponse,
	TaskGQLResponse,
)
from utils.db.dynamic_filter import get_filters

from .tasks import tasks_list_repository, tasks_repository


@strawberry.type
class PaginationWindow[T]:
	items: list[T] = strawberry.field(
		description="The list of items in this pagination window."
	)

	pagination_items: int = strawberry.field(
		description="Total number of items in the filtered dataset."
	)

	total_items: int = strawberry.field(description="Total data in the db")
	remaining_elements: int = strawberry.field(
		description="Remaining elements in the db"
	)


class Queries:
	async def all_tasks(
		self,
		info: strawberry.Info,
		limit: int,
		filter: str = "",
		offset: int = 0,
		order_by: str = "asc",
	) -> PaginationWindow[TasksType]:
		return await get_pagination_windows(
			order_by=order_by,
			limit=limit,
			offset=offset,
			schema=TaskGQLResponse,  # type: ignore
			model=tasks_repository,
			filter=filter,
			model_db=Tasks,  # type: ignore
			info=info,
		)

	async def all_tasks_list(
		self,
		info: strawberry.Info,
		limit: int,
		offset: int = 0,
		filter: str = "",
		order_by: str = "asc",
	) -> PaginationWindow[ListTaskType]:
		return await get_pagination_windows_task_list(
			model=tasks_list_repository,
			filter=filter,
			order_by=order_by,
			limit=limit,
			offset=offset,
			schema=ListTaskGQLResponse,  # type: ignore
			model_db=TaskList,  # type: ignore
			info=info,
		)


async def get_count(db: AsyncSession, model_db: Base) -> int:
	id_column = sa.literal_column("id")  # type: ignore

	stmt_count = lambda_stmt(
		lambda: sa.select(sa.func.count(id_column)),
	)
	stmt_count += lambda s: (s.select_from(model_db))
	result = await db.execute(stmt_count)
	count_result = result.scalars().all()
	return count_result[0]  # type: ignore


async def get_pagination_windows(
	info: strawberry.Info,
	model: Any,
	schema: BaseModel,
	limit: int,
	model_db: Base,
	return_type: Any | None = None,
	filter: str = "",
	offset: int = 0,
	order_by: str = "asc",
) -> PaginationWindow:  # type: ignore
	"""
	Get one pagination window on the given dataset for the given limit
	and offset, ordered by the given attribute and filtered using the
	given filters
	"""
	total_items = 0

	if limit <= 0 or limit > 100:
		raise Exception(f"limit ({limit}) must be between 0-100")
	filter_ = get_filters(filter, model_db)
	session: AsyncSession = info.context.db
	items, _ = await model.get_entity_pagination(
		filter=filter_, db=session, limit=limit, offset=offset, order_by=order_by
	)
	items = [schema.model_validate(item) for item in items]
	total_items = await get_count(session, model_db)

	total_items_count = len(items)
	remaining_elements = total_items - offset - total_items_count
	return PaginationWindow(
		items=items,
		pagination_items=total_items_count,
		total_items=total_items,
		remaining_elements=remaining_elements,
	)


def capitalize_enum_name(name: str) -> str:
	return " ".join(name.capitalize().split("_")) if "_" in name else name.capitalize()


async def get_pagination_windows_task_list(
	info: strawberry.Info,
	model: Any,
	schema: BaseModel,
	limit: int,
	model_db: Base,
	return_type: Any | None = None,
	filter: str = "",
	offset: int = 0,
	order_by: str = "asc",
) -> PaginationWindow:  # type: ignore
	"""
	Get one pagination window on the given dataset for the given limit
	and offset, ordered by the given attribute and filtered using the
	given filters
	"""
	total_items = 0

	if limit <= 0 or limit > 100:
		raise Exception(f"limit ({limit}) must be between 0-100")
	filter_ = get_filters(filter, model_db)
	session: AsyncSession = info.context.db
	kwargs = {}
	kwargs["join"] = lambda s: s.join(Tasks)
	items, _ = await model.get_entity_pagination(
		filter=filter_, db=session, limit=limit, offset=offset, order_by=order_by,
		**kwargs
	)
	tasks = []
	new_items = []

	for item in items:
		await session.refresh(item, attribute_names=["tasks"])
		tasks = [TaskGQLResponse.model_validate(t) for t in item.tasks]
		items_dict = item.__dict__
		items_dict["tasks"] = tasks
		new_items.append(schema.model_construct(**items_dict))
	items = new_items

	total_items = await get_count(session, model_db)

	total_items_count = len(items)
	remaining_elements = total_items - offset - total_items_count
	return PaginationWindow(
		items=items,
		pagination_items=total_items_count,
		total_items=total_items,
		remaining_elements=remaining_elements,
	)
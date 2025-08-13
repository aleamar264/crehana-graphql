from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import strawberry
from mock_tasks import TASK_DATA_MOCK

from models.models import TaskList, Tasks
from repository.query import (
	PaginationWindow,
	capitalize_enum_name,
	get_count,
	get_pagination_windows,
	get_pagination_windows_task_list,
)
from schema.grapql_schemas import ListTaskType, TasksType
from schema.tasks import TaskGQLResponse


@pytest.mark.asyncio
async def test_get_count(db):
	mock_result = Mock()
	mock_result.scalars.return_value.all.return_value = [1]
	db.execute.return_value = mock_result
	count = await get_count(db=db, model_db=Tasks)
	assert count == 1
	db.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_capitalize_enum_name():
	return_string = "Hello world"
	assert return_string == capitalize_enum_name("HELLO_WORLD")


@pytest.mark.asyncio
@patch("repository.query.get_count", return_value=1)
async def test_get_pagination_windows(db):
	info = MagicMock(spec=strawberry.Info)
	info.context.db = db
	mock_task_repository = AsyncMock()
	mock_task_repository.get_entity_pagination.return_value = (
		[Tasks(**TASK_DATA_MOCK[0])],
		1,
	)
	pagination: PaginationWindow[TasksType] = PaginationWindow(
		items=[TasksType(**TASK_DATA_MOCK[0])],
		pagination_items=1,
		total_items=1,
		remaining_elements=0,
	)

	return_pagination = await get_pagination_windows(
		order_by="asc",
		limit=10,
		offset=0,
		schema=TaskGQLResponse,  # type: ignore
		model=mock_task_repository,
		filter="",
		model_db=Tasks,  # type: ignore
		info=info,
	)

	assert pagination.total_items == return_pagination.total_items
	assert pagination.items[0].id == return_pagination.items[0].id


@pytest.mark.asyncio
@patch("repository.query.get_count", return_value=1)
async def test_get_pagination_windows_task_list(db):
	info = MagicMock(spec=strawberry.Info)
	info.context.db = db
	task = Tasks(**TASK_DATA_MOCK[0])
	mock_task_list_repository = AsyncMock()
	mock_task_list_repository.get_entity_pagination.return_value = (
		[
			TaskList(
				tasks=[task],
				id="0f115d4b-9fe3-4cfd-8339-7e5e49597167",
				name="List Test",
				created_at=datetime.now(UTC),
				updated_at=None,
			)
		],
		1,
	)
	pagination: PaginationWindow[ListTaskType] = PaginationWindow(
		items=[
			ListTaskType(
				tasks=[task],
				id="0f115d4b-9fe3-4cfd-8339-7e5e49597167",
				name="List Test",
				created_at=datetime.now(UTC),
				updated_at=None,
			)
		],
		pagination_items=1,
		total_items=1,
		remaining_elements=0,
	)

	return_pagination = await get_pagination_windows_task_list(
		order_by="asc",
		limit=10,
		offset=0,
		schema=TaskGQLResponse,  # type: ignore
		model=mock_task_list_repository,
		filter="",
		model_db=Tasks,  # type: ignore
		info=info,
	)

	assert pagination.total_items == return_pagination.total_items
	assert pagination.items[0].id == return_pagination.items[0].id

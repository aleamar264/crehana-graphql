from unittest.mock import AsyncMock, Mock

import pytest
from mock_tasks import TASK_DATA_MOCK
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Tasks
from schema.tasks import Status

TEST_TASKS = [
	Tasks(**TASK_DATA_MOCK[0]),
	Tasks(**TASK_DATA_MOCK[1]),
]


@pytest.fixture
def mock_db():
	"""Mocked AsyncSession with execute returning fake results."""
	mock_db = AsyncMock(spec=AsyncSession)

	# Configure the fake result
	mock_result = Mock()
	mock_result.scalars.return_value.all.return_value = TEST_TASKS
	mock_result.scalar_one_or_none.return_value = TEST_TASKS[0]

	mock_db.execute.return_value = mock_result
	return mock_db


@pytest.mark.asyncio
async def test_get_entity(repo, mock_db):
	filters = (Tasks.id == "6aa51c81-b757-4baa-928a-afa23b97e7a5",)

	result = await repo.get_entity(db=mock_db, filter=filters)

	mock_db.execute.assert_awaited()
	assert result == TEST_TASKS

	stmt = mock_db.execute.call_args[0][0]
	assert "id" in str(stmt)  # filter applied


@pytest.mark.asyncio
async def test_get_entity_pagination(repo, mock_db):
	mock_db.scalar.return_value = 2
	result = await repo.get_entity_pagination(
		db=mock_db, limit=5, offset=0, order_by="asc", filter=()
	)

	mock_db.execute.assert_awaited()
	assert result == (TEST_TASKS, 2)

	stmt = mock_db.execute.call_args[0][0]
	sql_text = str(stmt)
	assert "OFFSET" in sql_text and "LIMIT" in sql_text


@pytest.mark.asyncio
async def test_get_entity_by_id(repo, mock_db):
	result = await repo.get_entity_by_id(
		db=mock_db, entity_id="6aa51c81-b757-4baa-928a-afa23b97e7a8"
	)

	mock_db.execute.assert_awaited()
	assert result == TEST_TASKS[0]

	stmt = mock_db.execute.call_args[0][0]
	assert "id" in str(stmt)


@pytest.mark.asyncio
async def test_update_entity(repo, mock_db):
	result = await repo.update_entity(
		db=mock_db,
		entity_id="6aa51c81-b757-4baa-928a-afa23b97e7a8",
		entity_schema={"status": Status.COMPLETED},
		filter=(),
	)
	update_tasks = TEST_TASKS[0].__dict__
	update_tasks["status"] = Status.COMPLETED
	mock_db.execute.assert_awaited()
	assert result.status == update_tasks["status"]

	stmt = mock_db.execute.call_args[0][0]
	assert "id" in str(stmt)


@pytest.mark.asyncio
async def test_delete_entity(repo, mock_db):
	mock_db.execute.return_value.rowcount.return_value = 1
	result = await repo.delete_entity(
		db=mock_db,
		entity_id="6aa51c81-b757-4baa-928a-afa23b97e7a8",
		filter=(),
	)
	mock_db.execute.assert_awaited()
	assert result is None

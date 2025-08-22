from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.models import TaskList, Tasks
from repository.delete_mutation import delete_task, delete_task_list
from tests.mock_task_list import MOCK_TASK_LIST, MOCK_TASK_LIST_WITH_TASKS
from tests.mock_tasks import TASK_DATA_MOCK
from utils.exceptions import EntityDoesNotExistError


@pytest.mark.asyncio
@patch("repository.delete_mutation.tasks_repository.delete_entity", return_value=None)
async def test_delete_task_success(mock_delete_entity, strawberry_context):
	await delete_task(
		id="712260b0-2690-4da2-8bb4-75fd21628273", info=strawberry_context
	)


@pytest.mark.asyncio
@patch(
	"repository.delete_mutation.tasks_repository.delete_entity",
	side_effect=EntityDoesNotExistError("Entity don't exist"),
)
async def test_delete_task_failure(mock_delete_entity, strawberry_context):
	with pytest.raises(EntityDoesNotExistError) as exc:
		await delete_task(
			id="712260b0-2690-4da2-8bb4-75fd21628273", info=strawberry_context
		)
	assert str(exc.value) == "Entity don't exist"


@pytest.mark.asyncio
@patch(
	"repository.delete_mutation.tasks_list_repository.get_entity_by_id",
	return_value=TaskList(**MOCK_TASK_LIST),
)
@patch(
	"repository.delete_mutation.tasks_list_repository.delete_entity", return_value=None
)
async def test_delete_task_list_success(mock_delete_entity,mock_get_entity, strawberry_context):
	await delete_task_list(
		id="712260b0-2690-4da2-8bb4-75fd21628273", info=strawberry_context
	)

@pytest.mark.asyncio
@patch(
	"repository.delete_mutation.tasks_list_repository.get_entity_by_id",
	return_value=TaskList(**MOCK_TASK_LIST_WITH_TASKS),
)
@patch(
	"repository.delete_mutation.tasks_list_repository.delete_entity", return_value=None
)
@patch(
	"repository.delete_mutation.tasks_repository.update_entity", return_value=MagicMock()
)
async def test_delete_task_list_success_with_tasks(mock_update_entity, mock_delete_entity,mock_get_entity,strawberry_context, db):
	refresh = AsyncMock()
	refresh.return_value = Tasks(**TASK_DATA_MOCK[1])
	new_db = db.refresh.return_value = refresh
	strawberry_context.context.db = new_db
	await delete_task_list(
		id="712260b0-2690-4da2-8bb4-75fd21628273", info=strawberry_context
	)


@pytest.mark.asyncio
@patch(
	"repository.delete_mutation.tasks_list_repository.get_entity_by_id",
	side_effect=EntityDoesNotExistError("Entity don't exist"),
)
async def test_delete_task_list_failure(mock_get_entity,strawberry_context):
	with pytest.raises(EntityDoesNotExistError) as exc:
		await delete_task_list(
			id="712260b0-2690-4da2-8bb4-75fd21628273", info=strawberry_context
		)
	assert str(exc.value) == "Entity don't exist"

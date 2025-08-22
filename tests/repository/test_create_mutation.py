from enum import Enum
from unittest.mock import AsyncMock, patch

import pytest
from mock_tasks import TASK_DATA_MOCK
from mock_user import MOCK_USER

from models.models import TaskList, Tasks, Users
from repository.create_mutation import (
	convert_enum,
	get_other_entity,
	tasks_lists_mutation,
	tasks_mutation,
)
from schema.grapql_schemas import ListTaskInput, TasksInput
from tests.mock_task_list import (
	MOCK_TASK_LIST,
	MOCK_TASK_LIST_WITH_TASKS,
	MOCK_TASK_LIST_WITH_TASKS_ID,
)
from utils.exceptions import EntityAlreadyExistsError


@pytest.mark.asyncio
@pytest.mark.parametrize("return_value", [None, Tasks(**TASK_DATA_MOCK[0])])
async def test_get_other_entity_fail(return_value: None | Tasks, db: AsyncMock):
	crud = AsyncMock()
	crud.get_entity_by_args.return_value = return_value
	if return_value is None:
		await get_other_entity(
			column=Tasks.id,
			schema_value="50d5121d-2891-418d-bfc9-5c837322c5f6",
			db=db,
			crud=crud,
		)
	else:
		with pytest.raises(EntityAlreadyExistsError):
			await get_other_entity(
				column=Tasks.id,
				schema_value="50d5121d-2891-418d-bfc9-5c837322c5f6",
				db=db,
				crud=crud,
			)


def test_conver_enum():
	class TestEnum(Enum):
		TEST = "test"

	assert convert_enum(TestEnum.TEST) == "test"


@pytest.mark.asyncio
@patch(
	"repository.create_mutation.tasks_repository.create_entity",
	return_value=Tasks(**TASK_DATA_MOCK[1]),
)
@patch(
	"repository.create_mutation.user_repository.get_entity_by_id",
	return_value=Users(**MOCK_USER),
)
async def test_tasks(db: AsyncMock, strawberry_context: AsyncMock):
	task_input = TASK_DATA_MOCK[1].copy()
	task_input_id = task_input.pop("id")

	result = await tasks_mutation(
		tasks=TasksInput(**task_input), info=strawberry_context
	)
	assert task_input_id == result.id
	assert MOCK_USER["id"] == str(result.user)


@pytest.mark.asyncio
@patch(
	"repository.create_mutation.tasks_repository.create_entity",
	return_value=Tasks(**TASK_DATA_MOCK[1]),
)
async def test_tasks_user_none(db: AsyncMock, strawberry_context: AsyncMock):
	task_input = TASK_DATA_MOCK[1].copy()
	task_input_id = task_input.pop("id")
	task_input["user"] = None

	result = await tasks_mutation(
		tasks=TasksInput(**task_input), info=strawberry_context
	)
	assert task_input_id == result.id


@pytest.mark.asyncio
@patch(
	"repository.create_mutation.tasks_list_repository.create_entity",
	return_value=TaskList(**MOCK_TASK_LIST),
)
async def test_list_tasks_task_none(db: AsyncMock, strawberry_context: AsyncMock):
	list_task = MOCK_TASK_LIST.copy()
	del  list_task["id"]
	refresh = AsyncMock()
	refresh.return_value = None
	new_db = db.refresh.return_value = refresh
	strawberry_context.context.db = new_db
	result = await tasks_lists_mutation(
		tasks_list=ListTaskInput(**list_task), info=strawberry_context
	)
	assert MOCK_TASK_LIST["id"] == result.id

@pytest.mark.asyncio
@patch(
	"repository.create_mutation.tasks_list_repository.create_entity",
	return_value=TaskList(**MOCK_TASK_LIST_WITH_TASKS),
)
@patch(
	"repository.create_mutation.tasks_repository.get_entity_by_id",
	return_value=Tasks(**TASK_DATA_MOCK[1]),
)
async def test_list_tasks(mock_get_entity,mock_create_entity, db: AsyncMock, strawberry_context: AsyncMock):
	list_task = MOCK_TASK_LIST_WITH_TASKS_ID.copy()
	del  list_task["id"]
	refresh = AsyncMock()
	refresh.return_value = Tasks(**TASK_DATA_MOCK[1])
	db.refresh.return_value = refresh
	result = await tasks_lists_mutation(
		tasks_list=ListTaskInput(**list_task), info=strawberry_context
	)
	assert MOCK_TASK_LIST["id"] == result.id
	assert TASK_DATA_MOCK[1]["id"] == result.tasks[0].id

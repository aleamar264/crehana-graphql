from enum import Enum
from unittest.mock import AsyncMock, Mock, patch

import pytest
from mock_task_list import MOCK_TASK_LIST
from mock_tasks import TASK_DATA_MOCK

from models.models import TaskList, Tasks
from repository.update_mutation import (
	convert_enum,
	list_tasks_update,
	update_task_in_task_list,
	update_tasks,
)
from schema.grapql_schemas import ListTasksUpdate, StatusGQLEnum, TasksUpdateGQL
from schema.tasks import Status
from utils.fastapi.email.email_sender import fm

TASK_ID = "6ebdc61a-a2cf-4621-844e-a613cf15bbaf"
USER_ID = "8d2b2513-5fc4-45da-b36f-cf68567dc835"


def test_conver_enum():
	class TestEnum(Enum):
		TEST = "test"

	assert convert_enum(TestEnum.TEST) == "test"


@pytest.mark.asyncio
async def test_update_task_in_task_list(
	db_with: AsyncMock, strawberry_context: AsyncMock
):
	db_cm, session_mock = db_with
	tasks_mocks = Mock()
	tasks_mocks.task_list_id = ""
	mock_result = Mock()
	mock_result.scalars.return_value = (tasks_mocks,)
	session_mock.execute.return_value = mock_result

	strawberry_context.context.db = db_cm

	await update_task_in_task_list(
		tasks_ids=[""],
		id=TASK_ID,
		info=strawberry_context,
	)
	session_mock.execute.assert_awaited_once()
	session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_task(strawberry_context):
	data_to_update = TasksUpdateGQL(
		**{"status": StatusGQLEnum.ACTIVE, "title": "Test 2"}
	)
	data_to_return = TASK_DATA_MOCK[0].copy()
	data_to_return["status"] = Status.ACTIVE
	data_to_return["title"] = "Test 2"
	with patch(
		"repository.update_mutation.tasks_repository.update_entity",
		return_value=Tasks(**data_to_return),
	):
		task = await update_tasks(
			id=TASK_ID, tasks=data_to_update, info=strawberry_context
		)
	assert task.status == data_to_return["status"].value


@pytest.mark.asyncio
async def test_update_task_with_user(strawberry_context):
	data_to_update = TasksUpdateGQL(
		**{
			"status": StatusGQLEnum.ACTIVE,
			"title": "Test 2",
			"user": "8d2b2513-5fc4-45da-b36f-cf68567dc835",
		}
	)
	data_to_return = TASK_DATA_MOCK[0].copy()
	data_to_return["status"] = Status.ACTIVE
	data_to_return["title"] = "Test 2"
	data_to_return["user"] = USER_ID
	with (
		patch(
			"repository.update_mutation.tasks_repository.update_entity",
			return_value=Tasks(**data_to_return),
		),
		patch(
			"repository.update_mutation.user_repository.get_entity_by_id",
			return_value=Mock(email="test@example.com"),
		),
		patch(
			"repository.update_mutation.tasks_repository.get_entity_by_id",
			return_value=Tasks(**TASK_DATA_MOCK[0]),
		),
	):
		fm.config.SUPPRESS_SEND = 1
		task = await update_tasks(
			id=TASK_ID, tasks=data_to_update, info=strawberry_context
		)
	assert task.status == data_to_return["status"].value
	assert str(task.user) == data_to_return["user"]


@pytest.mark.asyncio
@patch(
	"repository.update_mutation.tasks_list_repository.update_entity",
	return_value=TaskList(**MOCK_TASK_LIST),
)
async def test_list_tasks_updates(
	mock_result_data, db_with: AsyncMock, strawberry_context
):
	db_cm, session_mock = db_with
	update_name = ListTasksUpdate(name="List Test 2")
	return_data = await list_tasks_update(
		id=MOCK_TASK_LIST["id"], info=strawberry_context, list_tasks=update_name
	)
	assert return_data.id == MOCK_TASK_LIST["id"]


@pytest.mark.asyncio
@patch(
	"repository.update_mutation.tasks_list_repository.update_entity",
	return_value=TaskList(**MOCK_TASK_LIST),
)
async def test_list_tasks_updates_with_tasks(
	mock_result_data, db: AsyncMock, strawberry_context
):
	task_to_return = TASK_DATA_MOCK[0].copy()
	task_to_return["tasks_list_id"] = MOCK_TASK_LIST["id"]
	db.refresh.return_value = Tasks(**TASK_DATA_MOCK[0])
	with patch(
		"repository.update_mutation.update_task_in_task_list",
		return_value=None,
	):
		update_name = ListTasksUpdate(name="List Test 2", tasks=[task_to_return["id"]])
		return_data = await list_tasks_update(
			id=MOCK_TASK_LIST["id"], info=strawberry_context, list_tasks=update_name
		)
		assert return_data.id == MOCK_TASK_LIST["id"]

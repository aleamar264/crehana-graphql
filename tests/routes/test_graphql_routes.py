from datetime import UTC, datetime
from unittest.mock import Mock, patch, AsyncMock
from uuid import UUID

import pytest
from mock_tasks import TASK_DATA_MOCK
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from strawberry.schema import Schema
from strawberry.schema.config import StrawberryConfig

from models.models import TaskList, Tasks, Users
from routes.graphql_route import Mutation, Query
from utils.fastapi.email.email_sender import fm
from mock_user import MOCK_USER
from mock_task_list import (
	MOCK_TASK_LIST,
	MOCK_TASK_LIST_WITH_TASKS,
	MOCK_TASK_LIST_WITH_TASKS_ID,
)
from schema.tasks import Status, Priority

schema = Schema(
	query=Query,
	mutation=Mutation,
	config=StrawberryConfig(auto_camel_case=False),
)


class DbContext(BaseContext):
	def __init__(self, db: AsyncSession):
		self.db = db
		# Await to retrieve the session instance, not the generator itself


async def get_context(db: AsyncSession) -> DbContext:
	"""This functions handle the dependency injection used by FastApi

	Args:
		db (AsyncSession, optional): Defaults to Depends(get_db_session).

	Returns:
		DbContext: Custom context
	"""
	return DbContext(db)


# ######################## QUERY #################################
# region Query


@pytest.mark.asyncio
async def test_query_route_tasks_fail():
	query = """
    query MyQuery {
    tasks(limit: 10) {
        items {
        id
        priority
        status
        }
    }
    }
    """
	result = await schema.execute(query=query)
	assert result.data is None
	assert result.errors[0].message == "An error occurred during authentication."


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
async def test_query_route_tasks_success(mock_auth, db: AsyncMock):
	query = """
    query MyQuery {
    tasks(limit: 10) {
    items {
        id
        priority
        status
    }
    total_items
    }
    }
    """
	mock_result = Mock()
	mock_result.scalars.return_value.all.side_effect = [
		[Tasks(**task) for task in TASK_DATA_MOCK],
		[2],
	]
	db.execute.return_value = mock_result

	result = await schema.execute(query=query, context_value=await get_context(db))
	assert result.data["tasks"]["items"][0]["priority"] == "CRITICAL"
	assert result.data["tasks"]["total_items"] == 2


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
async def test_query_route_list_tasks_without_tasks(mock_auth, db: AsyncMock):
	query = """
    query MyQuery {
    task_list(limit: 10) {
        items {
        created_at
        id
        }
        total_items
    }
    }
    """
	mock_result = Mock()
	mock_result.scalars.return_value.all.side_effect = [
		[
			TaskList(
				tasks=[],
				id="0f115d4b-9fe3-4cfd-8339-7e5e49597167",
				name="List Test",
				created_at=datetime.now(UTC),
				updated_at=None,
			)
		],
		[1],
	]
	db.execute.return_value = mock_result

	result = await schema.execute(query=query, context_value=await get_context(db))
	assert (
		result.data["task_list"]["items"][0]["id"]
		== "0f115d4b-9fe3-4cfd-8339-7e5e49597167"
	)
	assert result.data["task_list"]["total_items"] == 1


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
async def test_query_route_list_tasks_with_tasks(mock_auth, db: AsyncMock):
	query = """
query MyQuery {
  task_list(limit: 10) {
    items {
      created_at
      id
      tasks {
        title
        status
      }
    }
    total_items
  }
}
    """
	mock_result = Mock()
	mock_result.scalars.return_value.all.side_effect = [
		[
			TaskList(
				tasks=[Tasks(**task) for task in TASK_DATA_MOCK],
				id="0f115d4b-9fe3-4cfd-8339-7e5e49597167",
				name="List Test",
				created_at=datetime.now(UTC),
				updated_at=None,
			)
		],
		[1],
	]
	db.execute.return_value = mock_result
	db.refresh.side_effect = [Tasks(**task) for task in TASK_DATA_MOCK]
	result = await schema.execute(query=query, context_value=await get_context(db))
	assert (
		result.data["task_list"]["items"][0]["id"]
		== "0f115d4b-9fe3-4cfd-8339-7e5e49597167"
	)
	assert result.data["task_list"]["total_items"] == 1
	assert (
		result.data["task_list"]["items"][0]["tasks"][0]["title"]
		== TASK_DATA_MOCK[0]["title"]
	)


# ######################## MUTATIONS #################################
# ######################## CREATE #################################
# region Create


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.create_mutation.tasks_repository.create_entity")
async def test_mutation_route_create_task(mock_create_entity, mock_auth, db: AsyncMock):
	query = """
    mutation MyMutation {
    create_mutations {
    create_tasks(
        tasks: {status: NEW,
        priority: CRITICAL,
        title: "Test Task",
        description: "Some test description", }
    ) {
        status
        priority
        id
        title
    }
    }
    }"""

	fake_task = Tasks(**TASK_DATA_MOCK[0])
	mock_create_entity.return_value = fake_task
	result = await schema.execute(query=query, context_value=await get_context(db))
	assert not result.errors, result.errors


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.create_mutation.tasks_repository.create_entity")
@patch("repository.create_mutation.user_repository.get_entity_by_id")
async def test_mutation_route_create_task_user(
	mock_get_user, mock_create_entity, mock_auth, db: AsyncMock
):
	query = """
	mutation MyMutation{
	create_mutations {
	create_tasks(
		tasks: {status: NEW,
		priority: CRITICAL,
		title: "Test Task",
		description: "Some test description",
		user: "123e4567-e89b-12d3-a456-426614174000" }
	) {
		status
		priority
		id
		title
	}
	}
	}"""

	fake_task = Tasks(**TASK_DATA_MOCK[0])
	mock_create_entity.return_value = fake_task
	mock_get_user.return_value = Users(**MOCK_USER)
	fm.config.SUPPRESS_SEND = 1
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert mock_get_user.called
	assert mock_create_entity.called


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.create_mutation.tasks_list_repository.create_entity")
async def test_mutation_route_create_list_task(
	mock_create_entity, mock_auth, db: AsyncMock
):
	query = """
	mutation MyMutation {
  create_mutations {
    create_tasks_lists(tasks_list: {name: "Test list", tasks: []}) {
      id
      name
    }
  }
}"""

	fake_task = TaskList(**MOCK_TASK_LIST)
	mock_create_entity.return_value = fake_task
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert result.data["create_mutations"]["create_tasks_lists"]["name"] == "Test list"
	assert mock_create_entity.called


# ######################## MUTATIONS #################################
# ######################## Update #################################
# region Update


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.update_mutation.tasks_repository.update_entity")
async def test_mutation_route_update_task(mock_update_entity, mock_auth, db: AsyncMock):
	query = """
	mutation MyMutation {
  upadate_mutation {
    update_tasks_mutation(id: "6aa51c81-b757-4baa-928a-afa23b97e7a5",
	tasks: {
	status: NEW,
	priority: CRITICAL}) {
      priority
      status
    }
  }
}"""

	fake_task = Tasks(**TASK_DATA_MOCK[0])
	mock_update_entity.return_value = fake_task
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert mock_update_entity.called


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.update_mutation.tasks_repository.update_entity")
@patch("repository.update_mutation.tasks_repository.get_entity_by_id")
@patch("repository.update_mutation.user_repository.get_entity_by_id")
async def test_mutation_route_update_tasks_with_user(
	mock_get_entity, mock_get_task_entity, mock_update_entity, mock_auth, db: AsyncMock
):
	query = """
	mutation MyMutation {
  upadate_mutation {
    update_tasks_mutation(id: "6aa51c81-b757-4baa-928a-afa23b97e7a5",
	tasks: {
	status: NEW,
	priority: CRITICAL,
	user: "eca3933f-b9b8-4a18-b32f-4be052ce58ef"}) {
      priority
      status
    }
  }
}"""
	mock_get_task_entity.return_value = Tasks(**TASK_DATA_MOCK[0])
	update_tasks = TASK_DATA_MOCK[0].copy()
	update_tasks["user"] = UUID("eca3933f-b9b8-4a18-b32f-4be052ce58ef")
	mock_get_entity.return_value = Users(**MOCK_USER)
	fm.config.SUPPRESS_SEND = 1
	fake_task = Tasks(**update_tasks)
	mock_update_entity.return_value = fake_task
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert mock_update_entity.called


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.update_mutation.tasks_list_repository.update_entity")
async def test_mutation_route_update_task_list(
	mock_update_entity, mock_auth, db: AsyncMock
):
	query = """
	mutation MyMutation {
  upadate_mutation {
    list_tasks_update(
	id: "fbaa20cf-91aa-49db-bae9-105bc052421c",
	list_tasks: {name: "Update test"}) {
      id
      name
    }
  }
}
"""

	update_tasks = MOCK_TASK_LIST.copy()
	update_tasks["name"] = "Update test"
	fake_task = TaskList(**update_tasks)
	mock_update_entity.return_value = fake_task
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert mock_update_entity.called


@pytest.mark.asyncio
@patch("routes.graphql_route.IsAuthenticated.has_permission", return_value=True)
@patch("repository.update_mutation.tasks_list_repository.update_entity")
@patch("repository.update_mutation.update_task_in_task_list", return_value=None)
async def test_mutation_route_update_task_list_tasks(
	mock_update_tasks, mock_update_entity, mock_auth, db: AsyncMock
):
	query = """
	mutation MyMutation {
	upadate_mutation {
	list_tasks_update(
	id: "fbaa20cf-91aa-49db-bae9-105bc052421c",

	list_tasks: {name: "Update test",
	tasks: ["6aa51c81-b757-4baa-928a-afa23b97e7a5"]}) {
		id
		name
		tasks {
		id
			}
		}
	}
}
"""

	update_tasks = MOCK_TASK_LIST_WITH_TASKS.copy()
	update_tasks["name"] = "Update test"
	fake_task = TaskList(**update_tasks)
	mock_update_entity.return_value = fake_task
	result = await schema.execute(
		query=query,
		context_value=await get_context(db),
	)
	assert not result.errors, result.errors
	assert mock_update_entity.called


# ######################## MUTATIONS #################################
# ######################## Delete #################################
# region Delete

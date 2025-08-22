from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Tasks
from repository.repository import Repository


@pytest.fixture
def repo():
	r = Repository(Tasks)
	return r


@pytest.fixture
def db():
	return AsyncMock(spec=AsyncSession)


@pytest.fixture(scope="function")
def strawberry_context(db):
	info = AsyncMock()
	info.context.db = db
	yield info


@pytest.fixture
def db_with():
	"""Db with Context Manager"""
	session_mock = AsyncMock(spec=AsyncSession)

	# Create the context manager mock
	db_cm = AsyncMock()
	db_cm.__aenter__.return_value = session_mock
	db_cm.__aexit__.return_value = None

	return db_cm, session_mock

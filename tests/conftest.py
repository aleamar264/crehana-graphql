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
def strawberry_context():
	info = AsyncMock()
	info.context.db = db
	yield info

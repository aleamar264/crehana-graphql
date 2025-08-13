"""Test cases for user routes."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from schema.schemas import UserResponse
from utils.db.async_db_conf import depend_db_annotated
from utils.fastapi.auth import get_current_active_user

rest_client = TestClient(app)

TEST_USER_DATA = {
	"full_name": "Test User",
	"email": "test@example.com",
	"password": "Test@123!",
	"password2": "Test@123!",
}

MOCK_USER = {
	"id": "123e4567-e89b-12d3-a456-426614174000",
	"email": TEST_USER_DATA["email"],
	"full_name": TEST_USER_DATA["full_name"],
	"created_at": "2025-08-08T00:00:00Z",
	"updated_at": None,
}

db = AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_create_user_success():
	"""Test successful user creation."""

	app.dependency_overrides[depend_db_annotated] = db
	with patch("services.users.user_repository.create_entity") as mock_create:
		mock_user = UserResponse(**MOCK_USER)
		mock_create.return_value = mock_user

		response = rest_client.post("/users/register", json=TEST_USER_DATA)

		assert response.status_code == status.HTTP_201_CREATED
		assert response.json()["email"] == MOCK_USER["email"]
		assert response.json()["full_name"] == MOCK_USER["full_name"]
		app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_user_failure():
	"""Test user creation failure."""
	app.dependency_overrides[depend_db_annotated] = db
	with patch("services.users.user_repository.create_entity") as mock_create:
		mock_create.return_value = None
		response = rest_client.post("/users/register", json=TEST_USER_DATA)
		assert response.json()["_embedded"]["message"] == "Could not create user"
		assert response.status_code == status.HTTP_400_BAD_REQUEST
	app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_login_success():
	"""Test successful login."""
	form_data = {
		"username": TEST_USER_DATA["email"],
		"password": TEST_USER_DATA["password"],
	}

	app.dependency_overrides[depend_db_annotated] = db

	with patch("routes.user.authenticate_user") as mock_auth:
		mock_user = UserResponse(**MOCK_USER)
		mock_auth.return_value = mock_user

		response = rest_client.post("/users/token", data=form_data)

		assert response.status_code == status.HTTP_200_OK
		assert "access_token" in response.json()
		assert response.json()["token_type"] == "bearer"
	app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_login_failure():
	"""Test login failure."""
	form_data = {"username": "wrong@example.com", "password": "WrongPass@123!"}

	with patch("routes.user.authenticate_user", return_value=None):
		response = rest_client.post("/users/token", data=form_data)
		assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_read_users_me():
	"""Test reading current user profile."""
	mock_user = UserResponse(**MOCK_USER)
	app.dependency_overrides[get_current_active_user] = lambda: mock_user
	response = rest_client.get(
		"/users/me", headers={"Authorization": "Bearer test_token"}
	)
	assert response.status_code == status.HTTP_200_OK
	assert response.json()["email"] == MOCK_USER["email"]
	app.dependency_overrides = {}

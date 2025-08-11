"""Test cases for user routes."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest
from fastapi import status

from schema.schemas import UserResponse
from main import app

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


@pytest.mark.asyncio
async def test_create_user_success():
	"""Test successful user creation."""
	with patch("services.users.user_repository.create_entity") as mock_create:
		mock_user = AsyncMock()
		mock_create.return_value = mock_user

		response = rest_client.post("/users/register", json=TEST_USER_DATA)

		assert response.status_code == status.HTTP_201_CREATED
		assert response.json()["email"] == MOCK_USER["email"]
		assert response.json()["full_name"] == MOCK_USER["full_name"]


@pytest.mark.asyncio
async def test_create_user_failure():
	"""Test user creation failure."""
	with patch("services.users.user_repository.create_entity", return_value=None):
		response = rest_client.post("/users/register", json=TEST_USER_DATA)
		assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_login_success():
	"""Test successful login."""
	form_data = {
		"username": TEST_USER_DATA["email"],
		"password": TEST_USER_DATA["password"],
	}

	with patch("routes.user.authenticate_user") as mock_auth:
		mock_user = AsyncMock()
		mock_user.__dict__ = MOCK_USER
		mock_auth.return_value = mock_user

		response = rest_client.post("/users/token", data=form_data)

		assert response.status_code == status.HTTP_200_OK
		assert "access_token" in response.json()
		assert response.json()["token_type"] == "bearer"


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
	with patch("utils.fastapi.auth.get_current_active_user") as mock_get_user:
		mock_get_user.return_value = UserResponse(**MOCK_USER)

		response = rest_client.get(
			"/users/me", headers={"Authorization": "Bearer test_token"}
		)

		assert response.status_code == status.HTTP_200_OK
		assert response.json()["email"] == MOCK_USER["email"]


@pytest.mark.asyncio
async def test_read_own_items():
	"""Test reading user's items."""
	with patch("utils.fastapi.auth.get_current_active_user") as mock_get_user:
		mock_get_user.return_value = UserResponse(**MOCK_USER)

		response = rest_client.get(
			"/users/me/items", headers={"Authorization": "Bearer test_token"}
		)

		assert response.status_code == status.HTTP_200_OK
		assert response.json()[0]["owner"] == MOCK_USER["email"]


@pytest.mark.asyncio
async def test_read_users_me():
	"""Test reading current user profile."""
	with patch("utils.fastapi.auth.get_current_active_user") as mock_get_user:
		mock_get_user.return_value = UserResponse(**MOCK_USER)

		response = rest_client.get(
			"/users/me", headers={"Authorization": "Bearer test_token"}
		)

		assert response.status_code == status.HTTP_200_OK
		assert response.json()["email"] == MOCK_USER["email"]


@pytest.mark.asyncio
async def test_read_own_items():
	"""Test reading user's items."""
	with patch("utils.fastapi.auth.get_current_active_user") as mock_get_user:
		mock_get_user.return_value = UserResponse(**MOCK_USER)

		response = rest_client.get(
			"/users/me/items", headers={"Authorization": "Bearer test_token"}
		)

		assert response.status_code == status.HTTP_200_OK
		assert response.json()[0]["owner"] == MOCK_USER["email"]

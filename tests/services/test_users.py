from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from mock_user import MOCK_USER, TEST_USER_DATA
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Users as UserModels
from schema.schemas import UserWithPassword
from services.users import authenticate_user, get_user_by_email
from utils.exceptions import EntityDoesNotExistError


@pytest.mark.asyncio
async def test_get_user_by_email_success():
	"""Test get user by email"""
	db = AsyncMock(spec=AsyncSession)
	with patch("services.users.user_repository.get_entity_by_args") as patch_get_entity:
		patch_get_entity.return_value = UserModels(
			**MOCK_USER, password_hash="some_hash"
		)
		response = await get_user_by_email(db=db, email=TEST_USER_DATA["email"])
		assert response.id == UUID(MOCK_USER["id"])
		assert response.email == MOCK_USER["email"]


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
	db = AsyncMock(spec=AsyncSession)
	with pytest.raises(EntityDoesNotExistError) as exc:
		with patch(
			"services.users.user_repository.get_entity_by_args"
		) as patch_get_entity:
			patch_get_entity.return_value = None
			await get_user_by_email(db=db, email=TEST_USER_DATA["email"])
	assert str(exc.value) == f"The user with email {TEST_USER_DATA['email']} not exist"


@pytest.mark.asyncio
@patch("utils.fastapi.auth.verify_password", return_value=True)
@patch(
	"services.users.get_user_by_email",
	return_value=UserWithPassword(**MOCK_USER, password_hash="some_hash"),
)
async def test_authenticate_user_success(mock_verify_password, mock_get_user_by_email):
	db = AsyncMock(spec=AsyncSession)
	user = await authenticate_user(
		db=db, username=MOCK_USER["email"], password="secret_password"
	)
	assert user.email == MOCK_USER["email"]
	assert user.id == UUID(MOCK_USER["id"])

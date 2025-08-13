import re
from datetime import UTC, datetime
from typing import Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from utils.exceptions import GeneralError


class HealthCheck(BaseModel):
	status: str


class UserBase(BaseModel):
	"""
	Represents the basic attributes of a user.

	Attributes:
		full_name (str): Full name of the user.
		email (EmailStr): Email address of the user.
	"""

	full_name: str = Field(..., max_length=255, description="Full name of the user")
	email: EmailStr


class CreationPassword(BaseModel):
	"""
	Represents password creation attributes with validation.

	Attributes:
		password (str): The password to be created.
		password2 (str): Confirmation of the password.

	Methods:
		validate_password: Validates the password and ensures it meets security requirements.
	"""

	password: str = Field(..., min_length=8)
	password2: str = Field(..., min_length=8)

	@model_validator(mode="after")
	def validate_password(self) -> Self:
		pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+])[^\s]{8,20}$"
		if self.password != self.password2:
			raise GeneralError("Both password should be the same")
		if not re.fullmatch(pattern, self.password):
			raise GeneralError(
				"The password should be at leasts 8 long characters, and should contain\
					one o more special character (!@#$%^&*()_+)"
			)
		return self


class UserCreation(UserBase, CreationPassword):
	"""
	Represents the attributes required to create a new user.
	"""


class UserAttributes(BaseModel):
	"""
	Represents additional attributes of a user.

	Attributes:
		updated_at (datetime | None): Timestamp of the last update to the user's data.
		created_at (datetime): Timestamp of the user's creation.
	"""

	updated_at: datetime | None = None
	created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserSave(UserBase, UserAttributes):
	"""
	Represents the attributes required to save a user in the database.

	Attributes:
		password_hash (str): Hashed password of the user.
	"""

	password_hash: str = Field(...)


class UserResponse(UserBase, UserAttributes):
	"""
	Represents the attributes of a user in API responses.

	Attributes:
		id (UUID): Unique identifier for the user.
	"""

	id: UUID = Field(
		description="Unique identifier for the user", default_factory=uuid4
	)
	model_config = ConfigDict(from_attributes=True)


class UserWithPassword(UserResponse):
	password_hash: str = Field(...)


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	username: str

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from schema.schemas import Token, UserCreation, UserResponse, UserSave
from services.users import authenticate_user, user_repository
from utils.db.async_db_conf import depend_db_annotated
from utils.exceptions import GeneralError
from utils.fastapi.auth import (
	create_access_token,
	get_current_active_user,
	get_password_hash,
)

router = APIRouter(prefix="/users", tags=["user"])


SECRET_KEY = "b844c1b69c23aafeee875e5c41a317ee1d19b633f867da3b6f72f200ba31abe4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post(
	"/register",
	summary="Register new User",
	description="Register a new user",
	status_code=status.HTTP_201_CREATED,
	response_model=UserResponse,
)
async def create_user(
	body: UserCreation, db: depend_db_annotated, request: Request
) -> UserResponse:
	"""Register a new user in the system.

	Args:
		body (UserCreation): The user creation data including full_name, email, and password.
		db (AsyncSession): The database session dependency.
		request (Request): The FastAPI request object.

	Returns:
		UserResponse: The created user data without sensitive information.

	Raises:
		GeneralError: If the user creation fails.
	"""
	new_user = UserSave(
		**body.model_dump(exclude={"password", "password2"}),
		password_hash=get_password_hash(body.password),
	)
	user = await user_repository.create_entity(entity_schema=new_user, db=db)
	if not user:
		raise GeneralError(message="Could not create user")

	return UserResponse(**user.__dict__)


@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: depend_db_annotated
) -> Token:
	"""Authenticate a user and generate an access token.

	Args:
		form_data (OAuth2PasswordRequestForm): The OAuth2 form data containing username and password.
		db (AsyncSession): The database session dependency.

	Returns:
		Token: An object containing the access token and token type.

	Raises:
		HTTPException: If authentication fails with 401 status code.
	"""
	user = await authenticate_user(
		db=db, username=form_data.username, password=form_data.password
	)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		data={"sub": user.email}, expires_delta=access_token_expires
	)
	return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def read_users_me(
	current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> UserResponse:
	"""Get the current authenticated user's profile.

	Args:
		current_user (UserResponse): The current authenticated user, injected by the dependency.

	Returns:
		UserResponse: The current user's profile data.
	"""
	return current_user

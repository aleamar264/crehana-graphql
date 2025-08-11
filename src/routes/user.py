from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from schema.schemas import Token, UserCreation, UserResponse, UserSave
from services.users import authenticate_user, user_repository
from utils.db.async_db_conf import depend_db_annotated
from utils.exceptions import GeneralError, ServiceError
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
	try:
		new_user = UserSave(
			**body.model_dump(exclude={"password", "password2"}),
			password_hash=get_password_hash(body.password),
		)
		user = await user_repository.create_entity(entity_schema=new_user, db=db)
		if not user:
			raise GeneralError(message="Could not create user")

		return UserResponse(**user.__dict__)
	except Exception as e:
		raise ServiceError(message=f"Database error: {str(e)}")


@router.post("/token")
async def login_for_access_token(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: depend_db_annotated
) -> Token:
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
):
	return current_user


@router.get("/me/items")
async def read_own_items(
	current_user: Annotated[UserResponse, Depends(get_current_active_user)],
):
	return [{"item_id": "Foo", "owner": current_user.email}]

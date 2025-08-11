from models.models import Users as UserModels
from repository.repository import Repository
from schema.schemas import UserResponse, UserSave
from utils.db.async_db_conf import depend_db_annotated

user_repository = Repository(model=UserModels)


async def get_user_by_email(db: depend_db_annotated, email: str | int) -> UserResponse:
	user = await user_repository.get_entity_by_args(
		entity_schema_value=email, column=UserModels.email, db=db
	)
	user_dict = user.__dict__
	return UserResponse(**user_dict)


async def authenticate_user(db: depend_db_annotated, username: str, password: str):
	from utils.fastapi.auth import verify_password

	user = await get_user_by_email(db=db, email=username)
	if not user:
		return False
	if not verify_password(password, user.password_hash):
		return False
	return user
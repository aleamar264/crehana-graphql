from typing import Annotated, Any

import strawberry
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from graphql.error import GraphQLError
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext
from strawberry.permission import BasePermission

from utils.db.async_db_conf import get_db_session
from utils.exceptions import ServiceError
from utils.fastapi.auth import get_current_user
from utils.db.async_db_conf import depend_db_annotated

security = HTTPBearer()


class AuthenticationFailedGraphQL(GraphQLError):
	"""Custom exception for authentication failed"""

	def __init__(self, message: str, extensions: dict[str, Any] | None = None):
		if extensions is None:
			extensions = {}
		super().__init__(message, extensions=extensions)


class IsAuthenticated(BasePermission):
	message = "User is not authenticated/ doesn't have permission"
	error_extensions = {"code": "UNAUTHORIZED"}
	error_class = AuthenticationFailedGraphQL

	async def has_permission(
		self,
		source: Any,
		info: strawberry.Info,
		**kwargs: dict[str, Any],
	) -> bool:
		try:
			bearer_token: str = await get_request_dependencie(info.context.request)
			has_permission, _ = await get_back_permission_client(
				bearer_token, info.context.db
			)
			return has_permission
		except Exception as e:
			if isinstance(e, self.error_class):
				raise
			raise self.error_class(
				"An error occurred during authentication.",
				extensions={"code": "INTERNAL_ERROR", "details": str(e)},
			) from e


async def get_back_permission_client(
	credentials: str, db: depend_db_annotated
) -> tuple[bool, list[dict[str, Any]]]:
	await get_current_user(token=credentials, db=db)
	# If you hve a separate microservices
	# headers = {"Authorization": f"Bearer {credentials}"}
	# async with AsyncClient(base_url="http://localhost:9000/", headers=headers) as client:
	# 	response = await client.get("/api/v1/users/me")
	# 	if response.status_code != 200:
	# 		raise ServiceError(message="Server Error")
	return True, [{}]


async def get_request_dependencie(request: Request) -> str:
	"""This function returns the bearer token

	Args:
		request (Request): Request object

	Returns:
		str: Bearer token
	"""
	if "Authorization" not in request.headers:
		raise AuthenticationFailedGraphQL(
			message="User is not authenticated", extensions={"code": "UNAUTHORIZED"}
		)
	bearer_token: HTTPAuthorizationCredentials | None = await security(request)
	print(bearer_token)
	if bearer_token is None:
		raise AuthenticationFailedGraphQL(
			message="Bearer Token can't be empty", extensions={"code": "UNAUTHORIZED"}
		)
	return bearer_token.credentials


class DbContext(BaseContext):
	"""Custom context to use dependencies in FastAPI.

	>>> def __init__(self, dependencie_1, dependencie_2):
				self.dependencie_1 = dependencie_1
				self.dependencie_2 =  dependencie_2

	Args:
		BaseContext (BaseContext): Base class to create a dependency in fastapi using grahpql
	"""

	def __init__(
		self,
		db: AsyncSession,
	) -> None:
		self.db = db


async def get_context(
	# bearer_token: Annotated[str, Depends(get_request_dependencie)],
	db: Annotated[AsyncSession, Depends(get_db_session)],
	# back_permission: list[dict[str, Any]] = Depends(get_back_permission_client),
) -> DbContext:
	"""This functions handle the dependency injection used by FastApi

	Args:
		db (AsyncSession, optional): Defaults to Depends(get_db_session).

	Returns:
		DbContext: Custom context
	"""

	return DbContext(db=db)

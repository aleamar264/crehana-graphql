# mypy: ignore-errors
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from utils.exceptions import (
	AuthenticationFailed,
	EntityAlreadyExistsError,
	EntityDoesNotExistError,
	GeneralError,
	InvalidParameter,
	InvalidTokenError,
	ServiceError,
	TooManyRequest,
	create_exception_handler,
)
from utils.fastapi.base_url import get_base_url


async def validation_exception_handler(request: Request, exc: ValidationError):
	base = get_base_url(request)
	return JSONResponse(
		status_code=422,
		content={
			"_embedded": {
				"listErrors": [
					f"Invalid {error['loc'][0]} params: ['{error['loc'][1]}'] {error['msg'].lower()}"
					if len(error["loc"]) > 1
					else f"Missing {error['loc'][0]}. The {error['msg'].lower()}"
					for error in exc.errors()
				],
			},
			"_links": {"self": "".join((base, request.url.path))},
		},
	)


class CreateHandlerExceptions:
	def __init__(self, app: FastAPI):
		app.add_exception_handler(
			exc_class_or_status_code=EntityAlreadyExistsError,
			handler=create_exception_handler(
				status_code=status.HTTP_404_NOT_FOUND,
				initial_detail="User already registered",
			),
		)

		app.add_exception_handler(
			exc_class_or_status_code=ServiceError,
			handler=create_exception_handler(
				status.HTTP_500_INTERNAL_SERVER_ERROR,
				"A service seems to be down, try again later.",
			),
		)

		app.add_exception_handler(
			exc_class_or_status_code=AuthenticationFailed,
			handler=create_exception_handler(
				status.HTTP_401_UNAUTHORIZED,
				"The authentication failed. Wrong password/token",
			),
		)

		app.add_exception_handler(
			exc_class_or_status_code=InvalidTokenError,
			handler=create_exception_handler(
				status.HTTP_401_UNAUTHORIZED,
				"Invalid token, please re-authenticate again.",
			),
		)

		app.add_exception_handler(
			exc_class_or_status_code=EntityDoesNotExistError,
			handler=create_exception_handler(
				status.HTTP_404_NOT_FOUND,
				"Entity does not exist.",
			),
		)

		app.add_exception_handler(
			exc_class_or_status_code=GeneralError,
			handler=create_exception_handler(
				status.HTTP_400_BAD_REQUEST,
				"",
			),
		)
		app.add_exception_handler(
			exc_class_or_status_code=TooManyRequest,
			handler=create_exception_handler(
				status.HTTP_429_TOO_MANY_REQUESTS,
				"You have exceded the capacity of request for today.",
			),
		)
		app.add_exception_handler(
			exc_class_or_status_code=InvalidParameter,
			handler=create_exception_handler(
				status.HTTP_400_BAD_REQUEST,
				"The parameters sends are invalid.",
			),
		)
		app.add_exception_handler(
			exc_class_or_status_code=RequestValidationError,
			handler=validation_exception_handler,
		)

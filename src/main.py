import strawberry
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from strawberry.extensions import ParserCache
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from exception.handler_exception import CreateHandlerExceptions
from routes.graphql_route import Mutation, Query
from routes.user import router
from schema.schemas import HealthCheck
from utils.dependencies.graphql_fastapi import get_context

schema = strawberry.Schema(
	query=Query,
	mutation=Mutation,
	config=StrawberryConfig(auto_camel_case=False),
	extensions=[
		ParserCache(maxsize=5096),
	],
)
graphql_app = GraphQLRouter(
	schema=schema,
	context_getter=get_context,
)

# Create app
app = FastAPI(
	openapi_url="/openapi.json",
	docs_url="/docs",
	redoc_url="/redoc",
	root_path="/api/v1",
	title="Crehana Prueba tecnica",
	description="FastAPI application with GraphQL endpoints",
	version="1.0.0",
)

origin = ["*"]


app.add_middleware(
	CORSMiddleware,
	allow_origins=origin,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get(
	"/health",
	tags=["healthcheck"],
	summary="Perform a Health Check",
	response_description="Return HTTP Status Code 200 (OK)",
	status_code=status.HTTP_200_OK,
	response_model=HealthCheck,
)
def get_health() -> HealthCheck:
	"""
	## Perform a Health Check
	Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
	to ensure a robust container orchestration and management is in place. Other
	services which rely on proper functioning of the API service will not deploy if this
	endpoint returns any other HTTP status code except 200 (OK).
	Returns:
		HealthCheck: Returns a JSON response with the health status
	"""
	return HealthCheck(status="OK")


app.include_router(router=router)
app.include_router(graphql_app, prefix="/graphql")


CreateHandlerExceptions(app)

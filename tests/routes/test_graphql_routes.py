# """Test cases for GraphQL routes."""
# import pytest
# from strawberry.test import GraphQLClient
# from typing import AsyncGenerator

# from routes.graphql_route import Query, Mutation
# from schema.grapql_schemas import TasksType, ListTaskType
# from utils.dependencies.graphql_fastapi import IsAuthenticated

# @pytest.fixture
# async def graphql_client() -> AsyncGenerator[GraphQLClient, None]:
#     """Create a GraphQL client for testing."""
#     schema = await create_schema()
#     client = GraphQLClient(schema=schema)
#     yield client

# @pytest.mark.asyncio
# async def test_query_tasks(graphql_client: GraphQLClient):
#     """Test querying tasks."""
#     query = """
#     query {
#         tasks(first: 10) {
#             edges {
#                 node {
#                     id
#                     title
#                     status
#                     priority
#                 }
#             }
#         }
#     }
#     """

#     # Mock authentication
#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = True

#         response = await graphql_client.query(query)

#         assert "errors" not in response
#         assert "tasks" in response["data"]

# @pytest.mark.asyncio
# async def test_query_task_list(graphql_client: GraphQLClient):
#     """Test querying task lists."""
#     query = """
#     query {
#         taskList(first: 10) {
#             edges {
#                 node {
#                     id
#                     name
#                     tasks {
#                         id
#                         title
#                     }
#                 }
#             }
#         }
#     }
#     """

#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = True

#         response = await graphql_client.query(query)

#         assert "errors" not in response
#         assert "taskList" in response["data"]

# @pytest.mark.asyncio
# async def test_create_task_mutation(graphql_client: GraphQLClient):
#     """Test creating a task."""
#     mutation = """
#     mutation {
#         createMutations {
#             createTask(input: {
#                 title: "Test Task"
#                 description: "Test Description"
#                 status: NEW
#                 priority: MEDIUM
#             }) {
#                 id
#                 title
#                 status
#             }
#         }
#     }
#     """

#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = True

#         response = await graphql_client.query(mutation)

#         assert "errors" not in response
#         assert "createMutations" in response["data"]

# @pytest.mark.asyncio
# async def test_update_task_mutation(graphql_client: GraphQLClient):
#     """Test updating a task."""
#     mutation = """
#     mutation {
#         upadateMutation {
#             updateTask(id: "test-id", input: {
#                 title: "Updated Task"
#                 status: ACTIVE
#             }) {
#                 id
#                 title
#                 status
#             }
#         }
#     }
#     """

#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = True

#         response = await graphql_client.query(mutation)

#         assert "errors" not in response
#         assert "upadateMutation" in response["data"]

# @pytest.mark.asyncio
# async def test_delete_task_mutation(graphql_client: GraphQLClient):
#     """Test deleting a task."""
#     mutation = """
#     mutation {
#         deleteMutations {
#             deleteTask(id: "test-id")
#         }
#     }
#     """

#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = True

#         response = await graphql_client.query(mutation)

#         assert "errors" not in response
#         assert "deleteMutations" in response["data"]

# @pytest.mark.asyncio
# async def test_unauthorized_query(graphql_client: GraphQLClient):
#     """Test unauthorized access."""
#     query = """
#     query {
#         tasks(first: 10) {
#             edges {
#                 node {
#                     id
#                 }
#             }
#         }
#     }
#     """

#     with patch('utils.dependencies.graphql_fastapi.IsAuthenticated.__call__') as mock_auth:
#         mock_auth.return_value = False

#         response = await graphql_client.query(query)

#         assert "errors" in response

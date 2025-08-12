import pytest

import strawberry

from routes.graphql_route import Query
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from sqlalchemy.ext.asyncio import AsyncSession


schema = strawberry.Schema(query=Query)


@pytest.mark.asyncio
async def test_query_task():
    query = """
            query MyQuery {
        tasks(limit: 10) {
            items {
                id
                priority
                status
                }
            }
        }
        """
    mock_result = {
        "edges": [],
        "page_info": {"has_next_page": False, "has_previous_page": False},
    }
    patch("routes.graphql_route.Query.tasks", new=AsyncMock(return_value=mock_result))
    with patch(
        "routes.graphql_route.IsAuthenticated.has_permission") as permission_mock:
        permission_mock.has_permission.return_value = Mock(return_value=True)
        context = MagicMock()
        context.request = MagicMock()
        context.db = MagicMock(spec=AsyncSession())
        result = await schema.execute(query=query, context_value=context)
        assert not result.errors
        assert result.data == {}

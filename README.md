# Task Management API

A FastAPI-based task management system with user authentication and task organization capabilities.

## Features

### Task Management
- Create, read, update, and delete task lists
- Create, read, update, and delete tasks within a list
- Change task status
- List all tasks with filters by status or priority
- Task completion percentage tracking

### User Management
- JWT-based authentication
- User registration and login
- User task assignment
- Email notification simulation (mock implementation)

## Project Structure

### Models (`/models`)
- `Tasks`: Task entity with fields for status, priority, user assignment, and timestamps
- `TaskList`: Collection of tasks with name and timestamp fields
- `Users`: User entity with authentication and profile information

### Repository (`/repository`)
The repository layer implements CRUD operations with the following features:
- Generic repository pattern implementation
- Async database operations
- Pagination support
- Flexible filtering system

### Schema (`/schema`)
- `UserBase`: Base user attributes
- `UserCreation`: Schema for user registration
- `UserResponse`: Schema for API responses
- `Token`: JWT token schema
- Custom password validation with security requirements

### Services (`/services`)
- User authentication service
- Email-based user lookup
- Password verification

## Technical Details

### Authentication
- JWT token-based authentication
- Password hashing and verification
- Secure password requirements:
  - Minimum 8 characters
  - Special characters required
  - Mix of uppercase and lowercase
  - Numbers required

### Database
- PostgreSQL with SQLAlchemy ORM
- UUID primary keys
- Timestamped entities
- Foreign key relationships

### API Features
- Async/await pattern
- Type hints throughout
- Pydantic models for validation
- Comprehensive error handling

## Send email notifications (Dummy)
If when is created or updated one task and the field user is not None, this will trigger a notification by email,
in this case, this is suppressed to not generate any warning o crash the program.

## Dynamic Filtering System

The API includes a powerful dynamic filtering system (`dynamic_filter.py`) that supports both REST and GraphQL queries.

### Available Operators
```
=    Equal to
!=   Not equal to
>    Greater than
>=   Greater than or equal to
<    Less than
<=   Less than or equal to
like Pattern matching
in   Value in set
btw  Between values
```

### Filter Format
Filters are provided as a JSON-encoded string array where each filter is an array of [column_name, operator, value].

Example:
```python
# Single filter
filter = '[["id", "=", 1]]'

# Multiple filters
filter = '[["status", "=", "active"], ["created_at", ">=", "2025-01-01"]]'

# Between filter
filter = '[["age", "btw", [20, 30]]]'

# Relationship filter
filter = '[["tasks.status", "=", "ACTIVE"]]'
```

### GraphQL Integration
The filtering system seamlessly integrates with GraphQL queries:

```graphql
query {
  tasks(filter: "[["tasks.status", "=", "IN_PROGRESS"], ["tasks.priority", "=", "HIGH"]]") {
    id
    title
    status
    priority
  }
}
```

### Features
- Automatic type conversion for dates
- Dynamic column resolution
- Support for complex filtering conditions
- SQLAlchemy operator mapping
- Safe query construction

### Usage in Repository Layer
```python
# In your resolver
async def resolve_tasks(info, filter_str):
    filter_ = get_filters(filter_str, TaskModel)
    return await repository.get_entity(db=info.context.db, filter=filter_)
```



## Development

To run this file, you need to build the Docker compose called crehana-compose.yaml, to run this, use the command:
```shell
docker compose -f 'crehana-compose.yaml' up -d --build
```

This will create a container with the following services:
- PostgreSQL
- FastAPI
- Grafana
- Traefik
- Prometheus

To run the services of FastAPI you only need to go the http://localhost:9000/api/v1/docs or http://localhost:9000/api/v1/redoc.
Here you can create an user, login and generate an JWT token.

You can use the interfaz to log in or use directly the `/token` endpoint to generate the Bearer token.

With this token created you can use the GraphQL server http://localhost:9000/api/v1/graphql to Query and make some Mutations (Create, Delete, Update)

If you not add the Authorization Token you will receive an error.

### How to setup the env

For this project we will use UV from astral.

We can install in several ways [uv](https://docs.astral.sh/uv/getting-started/installation/) like using `pipx`, `curl` or `manual`, the recomendaded way to install is by curl.

When UV is installed, you can create the virtual envioronment using `uv sync`, this will install all the dependencies for the production and development.

In the `pyproject.toml` exist all the configurations, for Ruff, coverage, pytest, alembic and so on, so we don't need several files for each configuration.

### How to create the tables for db
To create the tables for the database, you need to had installed uv with the package of alembic.
From the route, where the `alembic.ini` exist alongside the `pyproject.toml`, you only need to run `uv run alembic upgrade head` to get the last version of the tables.

>[!WARNING]
> You need the docker compose running to not get any error.

### Run test
To run the test, you only need to run `uv run pytest`, this will take the configuration from `pyproject.toml`.
import strawberry
from strawberry.permission import PermissionExtension

from repository.create_mutation import CreateMutation
from repository.delete_mutation import DeleteMutation
from repository.query import PaginationWindow, Queries
from repository.update_mutation import UpdateMutation
from schema.grapql_schemas import ListTaskType, TasksType
from utils.dependencies.graphql_fastapi import IsAuthenticated


@strawberry.type

class Mutation:
	# 	"""Class that contain all the mutations (Create, Delete, Update)"""
	"""
	Mutation class containing all GraphQL mutation operations (Create, Delete, Update).

	Each mutation field is protected by authentication permissions, ensuring only authenticated users can perform these operations.

	Methods:
		create_mutations: Returns the CreateMutation object for handling create operations.
		delete_mutations: Returns the DeleteMutation object for handling delete operations.
		upadate_mutation: Returns the UpdateMutation object for handling update operations.
	"""

	@strawberry.field(extensions=[PermissionExtension(permissions=[IsAuthenticated()])])
	def create_mutations(self) -> CreateMutation:
		return CreateMutation()

	@strawberry.field(extensions=[PermissionExtension(permissions=[IsAuthenticated()])])
	def delete_mutations(self) -> DeleteMutation:
		return DeleteMutation()

	@strawberry.field(extensions=[PermissionExtension(permissions=[IsAuthenticated()])])
	def upadate_mutation(self) -> UpdateMutation:
		return UpdateMutation()


@strawberry.type
class Query:
	"""
	GraphQL Query class defining available queries for tasks.
	Attributes:
		tasks (PaginationWindow[TasksType]): Returns a paginated list of tasks. Requires authentication.
		task_list (PaginationWindow[ListTaskType]): Returns a paginated list of task summaries. Requires authentication.
	Each field uses a resolver from the Queries class and enforces authentication via permission_classes.
	"""
	tasks: PaginationWindow[TasksType] = strawberry.field(
		resolver=Queries.all_tasks, permission_classes=[IsAuthenticated]
	)
	task_list: PaginationWindow[ListTaskType] = strawberry.field(
		resolver=Queries.all_tasks_list, permission_classes=[IsAuthenticated]
	)

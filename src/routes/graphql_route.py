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
	"""All the gets"""

	tasks: PaginationWindow[TasksType] = strawberry.field(
		resolver=Queries.all_tasks, permission_classes=[IsAuthenticated]
	)
	task_list: PaginationWindow[ListTaskType] = strawberry.field(
		resolver=Queries.all_tasks_list, permission_classes=[IsAuthenticated]
	)

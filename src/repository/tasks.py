from models.models import TaskList, Tasks
from repository.repository import Repository

tasks_repository = Repository(model=Tasks)
tasks_list_repository = Repository(model=TaskList)

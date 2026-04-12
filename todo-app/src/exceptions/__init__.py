class TodoNotFoundError(Exception):
    def __init__(self, todo_id: str):
        self.todo_id = todo_id
        super().__init__(f"Todo with id '{todo_id}' not found.")


class TodoAlreadyExistsError(Exception):
    def __init__(self, todo_id: str):
        self.todo_id = todo_id
        super().__init__(f"Todo with id '{todo_id}' already exists.")


class InvalidTodoOperationError(Exception):
    pass

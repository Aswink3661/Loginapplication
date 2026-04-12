import type { Todo, TodoStatus, TodoUpdateRequest } from "../types/todo";
import { TodoItem } from "./TodoItem";

interface Props {
  todos: Todo[];
  loading: boolean;
  filterStatus: TodoStatus | "all";
  onUpdate: (id: string, payload: TodoUpdateRequest) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function TodoList({ todos, loading, filterStatus, onUpdate, onDelete }: Props) {
  const filtered =
    filterStatus === "all" ? todos : todos.filter((t) => t.status === filterStatus);

  if (loading) {
    return (
      <div className="state-container">
        <div className="spinner" />
        <p>Loading todos…</p>
      </div>
    );
  }

  if (filtered.length === 0) {
    return (
      <div className="state-container empty-state">
        <p>{filterStatus === "all" ? "No todos yet. Add one above!" : `No ${filterStatus.replace("_", " ")} todos.`}</p>
      </div>
    );
  }

  return (
    <ul className="todo-list">
      {filtered.map((todo) => (
        <li key={todo.id}>
          <TodoItem todo={todo} onUpdate={onUpdate} onDelete={onDelete} />
        </li>
      ))}
    </ul>
  );
}

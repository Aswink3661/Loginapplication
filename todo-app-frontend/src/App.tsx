import { useState } from "react";
import type { TodoStatus } from "./types/todo";
import { TodoFilters } from "./components/TodoFilters";
import { TodoForm } from "./components/TodoForm";
import { TodoList } from "./components/TodoList";
import { useTodos } from "./hooks/useTodos";

export default function App() {
  const { todos, total, page, totalPages, loading, error, fetchTodos, createTodo, updateTodo, deleteTodo, clearError } =
    useTodos();
  const [filterStatus, setFilterStatus] = useState<TodoStatus | "all">("all");

  const counts = {
    all: todos.length,
    pending: todos.filter((t) => t.status === "pending").length,
    in_progress: todos.filter((t) => t.status === "in_progress").length,
    done: todos.filter((t) => t.status === "done").length,
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📝 Todo App</h1>
        <span className="total-badge">{total} total</span>
      </header>

      <main className="app-main">
        {error && (
          <div className="alert alert-error">
            <span>{error}</span>
            <button onClick={clearError} className="alert-close">✕</button>
          </div>
        )}

        <TodoForm onSubmit={createTodo} />

        <div className="list-section">
          <TodoFilters activeStatus={filterStatus} onChange={setFilterStatus} counts={counts} />
          <TodoList
            todos={todos}
            loading={loading}
            filterStatus={filterStatus}
            onUpdate={updateTodo}
            onDelete={deleteTodo}
          />
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="btn btn-ghost"
              disabled={page === 1}
              onClick={() => fetchTodos(page - 1)}
            >
              ← Prev
            </button>
            <span>Page {page} of {totalPages}</span>
            <button
              className="btn btn-ghost"
              disabled={page === totalPages}
              onClick={() => fetchTodos(page + 1)}
            >
              Next →
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

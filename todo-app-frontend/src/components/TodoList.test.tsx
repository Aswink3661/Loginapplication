import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { TodoList } from "./TodoList";
import type { Todo, TodoUpdateRequest } from "../types/todo";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const makeTodo = (overrides: Partial<Todo> = {}): Todo => ({
  id: crypto.randomUUID(),
  title: "Default Todo",
  description: "",
  status: "pending",
  priority: "medium",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  ...overrides,
});

function renderList({
  todos = [] as Todo[],
  loading = false,
  filterStatus = "all" as Todo["status"] | "all",
  onUpdate = vi.fn() as (id: string, p: TodoUpdateRequest) => Promise<void>,
  onDelete = vi.fn() as (id: string) => Promise<void>,
} = {}) {
  render(
    <TodoList
      todos={todos}
      loading={loading}
      filterStatus={filterStatus}
      onUpdate={onUpdate}
      onDelete={onDelete}
    />
  );
}

// ---------------------------------------------------------------------------
// Loading state
// ---------------------------------------------------------------------------

describe("TodoList — loading", () => {
  it("shows a loading indicator when loading is true", () => {
    renderList({ loading: true });
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("does not render todo items while loading", () => {
    renderList({
      todos: [makeTodo({ title: "Hidden" })],
      loading: true,
    });
    expect(screen.queryByText("Hidden")).not.toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------

describe("TodoList — empty state", () => {
  it("shows empty prompt when there are no todos and filterStatus is 'all'", () => {
    renderList({ todos: [], filterStatus: "all" });
    expect(screen.getByText(/no todos yet/i)).toBeInTheDocument();
  });

  it("shows filtered empty message when filterStatus is set", () => {
    renderList({ todos: [], filterStatus: "done" });
    expect(screen.getByText(/no done todos/i)).toBeInTheDocument();
  });

  it("shows filtered empty message for in_progress", () => {
    renderList({ todos: [], filterStatus: "in_progress" });
    expect(screen.getByText(/no in progress todos/i)).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Rendering todos
// ---------------------------------------------------------------------------

describe("TodoList — rendering todos", () => {
  it("renders a list item for each todo", () => {
    renderList({
      todos: [makeTodo({ title: "A" }), makeTodo({ title: "B" })],
    });
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("B")).toBeInTheDocument();
  });

  it("renders a <ul> element", () => {
    renderList({ todos: [makeTodo()] });
    expect(screen.getByRole("list")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Filtering
// ---------------------------------------------------------------------------

describe("TodoList — filtering", () => {
  const todos = [
    makeTodo({ title: "Pending task", status: "pending" }),
    makeTodo({ title: "Done task", status: "done" }),
    makeTodo({ title: "WIP task", status: "in_progress" }),
  ];

  it("shows all todos when filterStatus is 'all'", () => {
    renderList({ todos, filterStatus: "all" });
    expect(screen.getByText("Pending task")).toBeInTheDocument();
    expect(screen.getByText("Done task")).toBeInTheDocument();
    expect(screen.getByText("WIP task")).toBeInTheDocument();
  });

  it("shows only pending todos when filterStatus is 'pending'", () => {
    renderList({ todos, filterStatus: "pending" });
    expect(screen.getByText("Pending task")).toBeInTheDocument();
    expect(screen.queryByText("Done task")).not.toBeInTheDocument();
    expect(screen.queryByText("WIP task")).not.toBeInTheDocument();
  });

  it("shows only done todos when filterStatus is 'done'", () => {
    renderList({ todos, filterStatus: "done" });
    expect(screen.getByText("Done task")).toBeInTheDocument();
    expect(screen.queryByText("Pending task")).not.toBeInTheDocument();
  });

  it("shows only in_progress todos when filterStatus is 'in_progress'", () => {
    renderList({ todos, filterStatus: "in_progress" });
    expect(screen.getByText("WIP task")).toBeInTheDocument();
    expect(screen.queryByText("Pending task")).not.toBeInTheDocument();
    expect(screen.queryByText("Done task")).not.toBeInTheDocument();
  });

  it("shows empty state when filter matches no todos", () => {
    renderList({ todos: [makeTodo({ status: "pending" })], filterStatus: "done" });
    expect(screen.getByText(/no done todos/i)).toBeInTheDocument();
  });
});

import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import { useTodos } from "./useTodos";
import { todoApi } from "../api/todoApi";
import type { Todo, PaginatedTodoResponse } from "../types/todo";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

vi.mock("../api/todoApi");

const mockTodo = (overrides: Partial<Todo> = {}): Todo => ({
  id: crypto.randomUUID(),
  title: "Test Todo",
  description: "",
  status: "pending",
  priority: "medium",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  ...overrides,
});

const mockPaginated = (items: Todo[]): PaginatedTodoResponse => ({
  items,
  total: items.length,
  page: 1,
  page_size: 20,
  total_pages: 1,
});

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("useTodos", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ---- initial fetch -------------------------------------------------------

  it("starts in loading state", () => {
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([]));
    const { result } = renderHook(() => useTodos());
    expect(result.current.loading).toBe(true);
  });

  it("populates todos after successful fetch", async () => {
    const todos = [mockTodo({ title: "A" }), mockTodo({ title: "B" })];
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated(todos));

    const { result } = renderHook(() => useTodos());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.todos).toHaveLength(2);
    expect(result.current.todos[0].title).toBe("A");
  });

  it("sets total from the API response", async () => {
    vi.mocked(todoApi.list).mockResolvedValue({
      ...mockPaginated([mockTodo()]),
      total: 42,
    });

    const { result } = renderHook(() => useTodos());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.total).toBe(42);
  });

  it("sets error when fetch fails", async () => {
    vi.mocked(todoApi.list).mockRejectedValue(new Error("Network error"));

    const { result } = renderHook(() => useTodos());

    await waitFor(() => expect(result.current.loading).toBe(false));

    expect(result.current.error).toBe("Network error");
    expect(result.current.todos).toHaveLength(0);
  });

  // ---- createTodo ----------------------------------------------------------

  it("adds a new todo to the list after createTodo", async () => {
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([]));
    const newTodo = mockTodo({ title: "Created" });
    vi.mocked(todoApi.create).mockResolvedValue(newTodo);

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.createTodo({ title: "Created" });
    });

    expect(result.current.todos).toContainEqual(expect.objectContaining({ title: "Created" }));
  });

  it("increments total after createTodo", async () => {
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([]));
    vi.mocked(todoApi.create).mockResolvedValue(mockTodo());

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.createTodo({ title: "New" });
    });

    expect(result.current.total).toBe(1);
  });

  // ---- updateTodo ----------------------------------------------------------

  it("updates an existing todo in the list", async () => {
    const todo = mockTodo({ title: "Old title" });
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([todo]));
    const updated = { ...todo, title: "New title" };
    vi.mocked(todoApi.update).mockResolvedValue(updated);

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.updateTodo(todo.id, { title: "New title" });
    });

    const found = result.current.todos.find((t) => t.id === todo.id);
    expect(found?.title).toBe("New title");
  });

  it("does not change total after updateTodo", async () => {
    const todo = mockTodo();
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([todo]));
    vi.mocked(todoApi.update).mockResolvedValue({ ...todo, status: "done" });

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    const totalBefore = result.current.total;
    await act(async () => {
      await result.current.updateTodo(todo.id, { status: "done" });
    });

    expect(result.current.total).toBe(totalBefore);
  });

  // ---- deleteTodo ----------------------------------------------------------

  it("removes todo from list after deleteTodo", async () => {
    const todo = mockTodo({ title: "Gone" });
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([todo]));
    vi.mocked(todoApi.delete).mockResolvedValue(undefined);

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.deleteTodo(todo.id);
    });

    expect(result.current.todos.find((t) => t.id === todo.id)).toBeUndefined();
  });

  it("decrements total after deleteTodo", async () => {
    const todo = mockTodo();
    vi.mocked(todoApi.list).mockResolvedValue(mockPaginated([todo]));
    vi.mocked(todoApi.delete).mockResolvedValue(undefined);

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.deleteTodo(todo.id);
    });

    expect(result.current.total).toBe(0);
  });

  // ---- fetchTodos (manual refresh) ----------------------------------------

  it("re-fetches todos on fetchTodos call", async () => {
    const first = [mockTodo({ title: "First" })];
    const second = [mockTodo({ title: "Refreshed" })];
    vi.mocked(todoApi.list)
      .mockResolvedValueOnce(mockPaginated(first))
      .mockResolvedValueOnce(mockPaginated(second));

    const { result } = renderHook(() => useTodos());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.fetchTodos(1);
    });

    expect(result.current.todos[0].title).toBe("Refreshed");
  });
});

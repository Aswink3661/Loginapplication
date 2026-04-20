import { describe, it, expect, vi, beforeEach } from "vitest";
import { todoApi } from "./todoApi";
import type { Todo, PaginatedTodoResponse } from "../types/todo";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const mockTodo: Todo = {
  id: "11111111-1111-1111-1111-111111111111",
  title: "Test Todo",
  description: "A description",
  status: "pending",
  priority: "medium",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

const mockPaginatedResponse: PaginatedTodoResponse = {
  items: [mockTodo],
  total: 1,
  page: 1,
  page_size: 20,
  total_pages: 1,
};

function mockFetch(body: unknown, status = 200) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(body),
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("todoApi", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  // ---- list ----------------------------------------------------------------

  describe("list", () => {
    it("calls the correct URL with default params", async () => {
      global.fetch = mockFetch(mockPaginatedResponse);

      await todoApi.list();

      expect(fetch).toHaveBeenCalledWith(
        "/api/v1/todos?page=1&page_size=20",
        expect.objectContaining({ headers: expect.any(Object) })
      );
    });

    it("passes custom page and pageSize", async () => {
      global.fetch = mockFetch(mockPaginatedResponse);

      await todoApi.list(3, 10);

      expect(fetch).toHaveBeenCalledWith(
        "/api/v1/todos?page=3&page_size=10",
        expect.anything()
      );
    });

    it("returns the paginated response", async () => {
      global.fetch = mockFetch(mockPaginatedResponse);

      const result = await todoApi.list();

      expect(result.items).toHaveLength(1);
      expect(result.total).toBe(1);
    });
  });

  // ---- get -----------------------------------------------------------------

  describe("get", () => {
    it("calls the correct URL", async () => {
      global.fetch = mockFetch(mockTodo);

      await todoApi.get(mockTodo.id);

      expect(fetch).toHaveBeenCalledWith(
        `/api/v1/todos/${mockTodo.id}`,
        expect.anything()
      );
    });

    it("returns the todo", async () => {
      global.fetch = mockFetch(mockTodo);

      const result = await todoApi.get(mockTodo.id);

      expect(result.title).toBe("Test Todo");
    });

    it("throws on 404", async () => {
      global.fetch = mockFetch({ detail: "Not found" }, 404);

      await expect(todoApi.get("bad-id")).rejects.toThrow("Not found");
    });
  });

  // ---- create --------------------------------------------------------------

  describe("create", () => {
    it("sends POST with JSON body", async () => {
      global.fetch = mockFetch(mockTodo, 201);

      await todoApi.create({ title: "New Todo", priority: "high" });

      expect(fetch).toHaveBeenCalledWith(
        "/api/v1/todos",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ title: "New Todo", priority: "high" }),
        })
      );
    });

    it("returns the created todo", async () => {
      global.fetch = mockFetch(mockTodo, 201);

      const result = await todoApi.create({ title: "New Todo" });

      expect(result.id).toBe(mockTodo.id);
    });

    it("throws when response is not ok", async () => {
      global.fetch = mockFetch({ detail: "Validation error" }, 422);

      await expect(todoApi.create({ title: "" })).rejects.toThrow("Validation error");
    });
  });

  // ---- update --------------------------------------------------------------

  describe("update", () => {
    it("sends PATCH to correct URL", async () => {
      global.fetch = mockFetch(mockTodo);

      await todoApi.update(mockTodo.id, { status: "done" });

      expect(fetch).toHaveBeenCalledWith(
        `/api/v1/todos/${mockTodo.id}`,
        expect.objectContaining({ method: "PATCH" })
      );
    });

    it("sends update payload as JSON body", async () => {
      global.fetch = mockFetch(mockTodo);

      await todoApi.update(mockTodo.id, { title: "Updated", status: "done" });

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ title: "Updated", status: "done" }),
        })
      );
    });

    it("returns the updated todo", async () => {
      const updated = { ...mockTodo, status: "done" as const };
      global.fetch = mockFetch(updated);

      const result = await todoApi.update(mockTodo.id, { status: "done" });

      expect(result.status).toBe("done");
    });
  });

  // ---- delete --------------------------------------------------------------

  describe("delete", () => {
    it("sends DELETE to correct URL", async () => {
      global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 204, json: vi.fn() });

      await todoApi.delete(mockTodo.id);

      expect(fetch).toHaveBeenCalledWith(
        `/api/v1/todos/${mockTodo.id}`,
        expect.objectContaining({ method: "DELETE" })
      );
    });

    it("resolves without value on 204", async () => {
      global.fetch = vi.fn().mockResolvedValue({ ok: true, status: 204, json: vi.fn() });

      const result = await todoApi.delete(mockTodo.id);

      expect(result).toBeUndefined();
    });

    it("throws on 404", async () => {
      global.fetch = mockFetch({ detail: "Not found" }, 404);

      await expect(todoApi.delete("bad-id")).rejects.toThrow("Not found");
    });
  });

  // ---- error handling ------------------------------------------------------

  describe("error handling", () => {
    it("falls back to 'Unknown error' when body cannot be parsed", async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: vi.fn().mockRejectedValue(new Error("not json")),
      });

      // The api catches json() failure and falls back to { detail: "Unknown error" }
      await expect(todoApi.list()).rejects.toThrow("Unknown error");
    });

    it("sets Content-Type header on all requests", async () => {
      global.fetch = mockFetch(mockPaginatedResponse);

      await todoApi.list();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({ "Content-Type": "application/json" }),
        })
      );
    });
  });
});

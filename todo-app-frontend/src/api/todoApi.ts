import type {
  PaginatedTodoResponse,
  Todo,
  TodoCreateRequest,
  TodoUpdateRequest,
} from "../types/todo";

const BASE_URL = "/api/v1";

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }

  // 204 No Content — nothing to parse
  if (res.status === 204) return undefined as unknown as T;

  return res.json() as Promise<T>;
}

export const todoApi = {
  list(page = 1, pageSize = 20): Promise<PaginatedTodoResponse> {
    return request(`/todos?page=${page}&page_size=${pageSize}`);
  },

  get(id: string): Promise<Todo> {
    return request(`/todos/${id}`);
  },

  create(payload: TodoCreateRequest): Promise<Todo> {
    return request<Todo>("/todos", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  update(id: string, payload: TodoUpdateRequest): Promise<Todo> {
    return request<Todo>(`/todos/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  delete(id: string): Promise<void> {
    return request<void>(`/todos/${id}`, { method: "DELETE" });
  },
};

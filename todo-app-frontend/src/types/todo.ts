export type TodoStatus = "pending" | "in_progress" | "done";
export type TodoPriority = "low" | "medium" | "high";

export interface Todo {
  id: string;
  title: string;
  description: string;
  status: TodoStatus;
  priority: TodoPriority;
  created_at: string;
  updated_at: string;
}

export interface PaginatedTodoResponse {
  items: Todo[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface TodoCreateRequest {
  title: string;
  description?: string;
  priority?: TodoPriority;
}

export interface TodoUpdateRequest {
  title?: string;
  description?: string;
  status?: TodoStatus;
  priority?: TodoPriority;
}

export interface ApiError {
  detail: string;
}

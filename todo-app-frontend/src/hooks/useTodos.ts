import { useCallback, useEffect, useReducer } from "react";
import { todoApi } from "../api/todoApi";
import type { Todo, TodoCreateRequest, TodoUpdateRequest } from "../types/todo";

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

interface State {
  todos: Todo[];
  total: number;
  page: number;
  totalPages: number;
  loading: boolean;
  error: string | null;
}

const initialState: State = {
  todos: [],
  total: 0,
  page: 1,
  totalPages: 1,
  loading: false,
  error: null,
};

// ---------------------------------------------------------------------------
// Reducer
// ---------------------------------------------------------------------------

type Action =
  | { type: "FETCH_START" }
  | { type: "FETCH_SUCCESS"; payload: { todos: Todo[]; total: number; page: number; totalPages: number } }
  | { type: "FETCH_ERROR"; payload: string }
  | { type: "ADD_TODO"; payload: Todo }
  | { type: "UPDATE_TODO"; payload: Todo }
  | { type: "REMOVE_TODO"; payload: string }
  | { type: "CLEAR_ERROR" };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, loading: true, error: null };
    case "FETCH_SUCCESS":
      return {
        ...state,
        loading: false,
        todos: action.payload.todos,
        total: action.payload.total,
        page: action.payload.page,
        totalPages: action.payload.totalPages,
      };
    case "FETCH_ERROR":
      return { ...state, loading: false, error: action.payload };
    case "ADD_TODO":
      return { ...state, todos: [action.payload, ...state.todos], total: state.total + 1 };
    case "UPDATE_TODO":
      return {
        ...state,
        todos: state.todos.map((t) => (t.id === action.payload.id ? action.payload : t)),
      };
    case "REMOVE_TODO":
      return {
        ...state,
        todos: state.todos.filter((t) => t.id !== action.payload),
        total: state.total - 1,
      };
    case "CLEAR_ERROR":
      return { ...state, error: null };
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useTodos() {
  const [state, dispatch] = useReducer(reducer, initialState);

  const fetchTodos = useCallback(async (page = 1) => {
    dispatch({ type: "FETCH_START" });
    try {
      const data = await todoApi.list(page);
      dispatch({
        type: "FETCH_SUCCESS",
        payload: {
          todos: data.items,
          total: data.total,
          page: data.page,
          totalPages: data.total_pages,
        },
      });
    } catch (err) {
      dispatch({ type: "FETCH_ERROR", payload: (err as Error).message });
    }
  }, []);

  const createTodo = useCallback(async (payload: TodoCreateRequest) => {
    const todo = await todoApi.create(payload);
    dispatch({ type: "ADD_TODO", payload: todo });
  }, []);

  const updateTodo = useCallback(async (id: string, payload: TodoUpdateRequest) => {
    const todo = await todoApi.update(id, payload);
    dispatch({ type: "UPDATE_TODO", payload: todo });
  }, []);

  const deleteTodo = useCallback(async (id: string) => {
    await todoApi.delete(id);
    dispatch({ type: "REMOVE_TODO", payload: id });
  }, []);

  const clearError = useCallback(() => dispatch({ type: "CLEAR_ERROR" }), []);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return {
    ...state,
    fetchTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    clearError,
  };
}

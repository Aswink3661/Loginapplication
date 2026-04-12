import { useState } from "react";
import type { Todo, TodoPriority, TodoStatus, TodoUpdateRequest } from "../types/todo";

interface Props {
  todo: Todo;
  onUpdate: (id: string, payload: TodoUpdateRequest) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

const STATUS_LABELS: Record<TodoStatus, string> = {
  pending: "Pending",
  in_progress: "In Progress",
  done: "Done",
};

const PRIORITY_LABELS: Record<TodoPriority, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
};

export function TodoItem({ todo, onUpdate, onDelete }: Props) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(todo.title);
  const [description, setDescription] = useState(todo.description);
  const [busy, setBusy] = useState(false);

  const handleStatusChange = async (status: TodoStatus) => {
    setBusy(true);
    try {
      await onUpdate(todo.id, { status });
    } finally {
      setBusy(false);
    }
  };

  const handlePriorityChange = async (priority: TodoPriority) => {
    setBusy(true);
    try {
      await onUpdate(todo.id, { priority });
    } finally {
      setBusy(false);
    }
  };

  const handleSave = async () => {
    if (!title.trim()) return;
    setBusy(true);
    try {
      await onUpdate(todo.id, { title: title.trim(), description: description.trim() });
      setEditing(false);
    } finally {
      setBusy(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${todo.title}"?`)) return;
    setBusy(true);
    try {
      await onDelete(todo.id);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`todo-item priority-${todo.priority} ${todo.status === "done" ? "done" : ""}`}>
      <div className="todo-item-header">
        {editing ? (
          <input
            className="input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
          />
        ) : (
          <span className="todo-title">{todo.title}</span>
        )}
        <div className="todo-badges">
          <span className={`badge badge-priority-${todo.priority}`}>
            {PRIORITY_LABELS[todo.priority]}
          </span>
          <span className={`badge badge-status-${todo.status}`}>
            {STATUS_LABELS[todo.status]}
          </span>
        </div>
      </div>

      {editing ? (
        <textarea
          className="textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          maxLength={1000}
        />
      ) : (
        todo.description && <p className="todo-description">{todo.description}</p>
      )}

      <div className="todo-item-footer">
        <div className="todo-controls">
          <select
            className="select select-sm"
            value={todo.status}
            onChange={(e) => handleStatusChange(e.target.value as TodoStatus)}
            disabled={busy}
          >
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <select
            className="select select-sm"
            value={todo.priority}
            onChange={(e) => handlePriorityChange(e.target.value as TodoPriority)}
            disabled={busy}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div className="todo-actions">
          {editing ? (
            <>
              <button className="btn btn-sm btn-success" onClick={handleSave} disabled={busy}>
                Save
              </button>
              <button className="btn btn-sm btn-ghost" onClick={() => { setEditing(false); setTitle(todo.title); setDescription(todo.description); }}>
                Cancel
              </button>
            </>
          ) : (
            <button className="btn btn-sm btn-ghost" onClick={() => setEditing(true)} disabled={busy}>
              Edit
            </button>
          )}
          <button className="btn btn-sm btn-danger" onClick={handleDelete} disabled={busy}>
            Delete
          </button>
        </div>
      </div>
      <span className="todo-date">
        Created {new Date(todo.created_at).toLocaleDateString()}
      </span>
    </div>
  );
}

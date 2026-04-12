import { useState } from "react";
import type { TodoCreateRequest, TodoPriority } from "../types/todo";

interface Props {
  onSubmit: (payload: TodoCreateRequest) => Promise<void>;
}

export function TodoForm({ onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<TodoPriority>("medium");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSubmit({ title: title.trim(), description: description.trim(), priority });
      setTitle("");
      setDescription("");
      setPriority("medium");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="todo-form" onSubmit={handleSubmit}>
      <h2>New Todo</h2>
      {error && <p className="form-error">{error}</p>}
      <div className="form-row">
        <input
          className="input"
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          required
        />
        <select
          className="select"
          value={priority}
          onChange={(e) => setPriority(e.target.value as TodoPriority)}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? "Adding…" : "Add"}
        </button>
      </div>
      <textarea
        className="textarea"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        maxLength={1000}
        rows={2}
      />
    </form>
  );
}

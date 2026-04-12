import type { TodoStatus } from "../types/todo";

interface Props {
  activeStatus: TodoStatus | "all";
  onChange: (status: TodoStatus | "all") => void;
  counts: Record<string, number>;
}

const FILTERS: { value: TodoStatus | "all"; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "in_progress", label: "In Progress" },
  { value: "done", label: "Done" },
];

export function TodoFilters({ activeStatus, onChange, counts }: Props) {
  return (
    <div className="todo-filters">
      {FILTERS.map((f) => (
        <button
          key={f.value}
          className={`filter-btn ${activeStatus === f.value ? "active" : ""}`}
          onClick={() => onChange(f.value)}
        >
          {f.label}
          {counts[f.value] !== undefined && (
            <span className="filter-count">{counts[f.value]}</span>
          )}
        </button>
      ))}
    </div>
  );
}

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodoItem } from "./TodoItem";
import type { Todo } from "../types/todo";

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

const baseTodo: Todo = {
  id: "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  title: "Test Todo",
  description: "A test description",
  status: "pending",
  priority: "medium",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
};

function renderItem(
  overrides: Partial<Todo> = {},
  onUpdate = vi.fn().mockResolvedValue(undefined),
  onDelete = vi.fn().mockResolvedValue(undefined)
) {
  const todo = { ...baseTodo, ...overrides };
  render(<TodoItem todo={todo} onUpdate={onUpdate} onDelete={onDelete} />);
  return { todo, onUpdate, onDelete };
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("TodoItem — rendering", () => {
  it("displays the todo title", () => {
    renderItem();
    expect(screen.getByText("Test Todo")).toBeInTheDocument();
  });

  it("displays the todo description", () => {
    renderItem();
    expect(screen.getByText("A test description")).toBeInTheDocument();
  });

  it("does not render empty description", () => {
    renderItem({ description: "" });
    expect(screen.queryByRole("paragraph")).not.toBeInTheDocument();
  });

  it("shows priority badge", () => {
    renderItem({ priority: "high" });
    // badge span and select option both contain the label — target the badge span
    const badge = document.querySelector(".badge-priority-high");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent("High");
  });

  it("shows status badge", () => {
    renderItem({ status: "in_progress" });
    const badge = document.querySelector(".badge-status-in_progress");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveTextContent("In Progress");
  });

  it("applies done class when status is done", () => {
    const { container } = render(
      <TodoItem
        todo={{ ...baseTodo, status: "done" }}
        onUpdate={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(container.querySelector(".done")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Status change
// ---------------------------------------------------------------------------

describe("TodoItem — status select", () => {
  it("renders a status select", () => {
    renderItem();
    expect(screen.getByDisplayValue("Pending")).toBeInTheDocument();
  });

  it("calls onUpdate with new status when changed", async () => {
    const user = userEvent.setup();
    const { onUpdate } = renderItem();

    await user.selectOptions(screen.getByDisplayValue("Pending"), "done");

    expect(onUpdate).toHaveBeenCalledWith(baseTodo.id, { status: "done" });
  });
});

// ---------------------------------------------------------------------------
// Priority change
// ---------------------------------------------------------------------------

describe("TodoItem — priority select", () => {
  it("renders a priority select", () => {
    renderItem();
    expect(screen.getByDisplayValue("Medium")).toBeInTheDocument();
  });

  it("calls onUpdate with new priority when changed", async () => {
    const user = userEvent.setup();
    const { onUpdate } = renderItem();

    await user.selectOptions(screen.getByDisplayValue("Medium"), "high");

    expect(onUpdate).toHaveBeenCalledWith(baseTodo.id, { priority: "high" });
  });
});

// ---------------------------------------------------------------------------
// Editing
// ---------------------------------------------------------------------------

describe("TodoItem — edit mode", () => {
  it("enters edit mode when Edit button is clicked", async () => {
    const user = userEvent.setup();
    renderItem();

    await user.click(screen.getByRole("button", { name: /edit/i }));

    expect(screen.getByDisplayValue("Test Todo")).toBeInTheDocument();
  });

  it("saves updated title on Save", async () => {
    const user = userEvent.setup();
    const { onUpdate } = renderItem();

    await user.click(screen.getByRole("button", { name: /edit/i }));
    const titleInput = screen.getByDisplayValue("Test Todo");
    await user.clear(titleInput);
    await user.type(titleInput, "Updated Title");
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(onUpdate).toHaveBeenCalledWith(
      baseTodo.id,
      expect.objectContaining({ title: "Updated Title" })
    );
  });

  it("does not save when title is blank", async () => {
    const user = userEvent.setup();
    const { onUpdate } = renderItem();

    await user.click(screen.getByRole("button", { name: /edit/i }));
    const titleInput = screen.getByDisplayValue("Test Todo");
    await user.clear(titleInput);
    await user.click(screen.getByRole("button", { name: /save/i }));

    expect(onUpdate).not.toHaveBeenCalled();
  });

  it("cancels edit mode on Cancel", async () => {
    const user = userEvent.setup();
    renderItem();

    await user.click(screen.getByRole("button", { name: /edit/i }));
    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(screen.getByText("Test Todo")).toBeInTheDocument();
    expect(screen.queryByDisplayValue("Test Todo")).not.toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Deletion
// ---------------------------------------------------------------------------

describe("TodoItem — delete", () => {
  beforeEach(() => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  it("calls onDelete with todo id when confirmed", async () => {
    const user = userEvent.setup();
    const { onDelete } = renderItem();

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(onDelete).toHaveBeenCalledWith(baseTodo.id);
  });

  it("does not call onDelete when cancelled", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const user = userEvent.setup();
    const { onDelete } = renderItem();

    await user.click(screen.getByRole("button", { name: /delete/i }));

    expect(onDelete).not.toHaveBeenCalled();
  });
});

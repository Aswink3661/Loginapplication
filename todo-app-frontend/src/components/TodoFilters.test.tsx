import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodoFilters } from "./TodoFilters";
import type { TodoStatus } from "../types/todo";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const allStatuses: (TodoStatus | "all")[] = ["all", "pending", "in_progress", "done"];

const defaultCounts = { all: 10, pending: 4, in_progress: 3, done: 3 };

function renderFilters(
  activeStatus: TodoStatus | "all" = "all",
  onChange = vi.fn(),
  counts = defaultCounts
) {
  render(
    <TodoFilters activeStatus={activeStatus} onChange={onChange} counts={counts} />
  );
  return { onChange };
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("TodoFilters — rendering", () => {
  it("renders all four filter buttons", () => {
    renderFilters();
    expect(screen.getByRole("button", { name: /all/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /pending/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /in progress/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /done/i })).toBeInTheDocument();
  });

  it.each(allStatuses)("marks '%s' button as active when it is the active filter", (status) => {
    renderFilters(status);
    const btn = screen.getAllByRole("button").find((b) =>
      b.classList.contains("active")
    );
    expect(btn).toBeTruthy();
  });

  it("shows counts next to each filter", () => {
    renderFilters();
    expect(screen.getByText("10")).toBeInTheDocument(); // all
    expect(screen.getByText("4")).toBeInTheDocument();  // pending
    // both in_progress and done have count 3 — two spans expected
    expect(screen.getAllByText("3")).toHaveLength(2);
  });

  it("does not crash when counts object is empty", () => {
    expect(() => renderFilters("all", vi.fn(), {} as typeof defaultCounts)).not.toThrow();
  });
});

// ---------------------------------------------------------------------------
// Interaction
// ---------------------------------------------------------------------------

describe("TodoFilters — interaction", () => {
  it("calls onChange with 'all' when All is clicked", async () => {
    const user = userEvent.setup();
    const { onChange } = renderFilters("pending");

    await user.click(screen.getByRole("button", { name: /all/i }));

    expect(onChange).toHaveBeenCalledWith("all");
  });

  it("calls onChange with 'pending' when Pending is clicked", async () => {
    const user = userEvent.setup();
    const { onChange } = renderFilters();

    await user.click(screen.getByRole("button", { name: /pending/i }));

    expect(onChange).toHaveBeenCalledWith("pending");
  });

  it("calls onChange with 'in_progress' when In Progress is clicked", async () => {
    const user = userEvent.setup();
    const { onChange } = renderFilters();

    await user.click(screen.getByRole("button", { name: /in progress/i }));

    expect(onChange).toHaveBeenCalledWith("in_progress");
  });

  it("calls onChange with 'done' when Done is clicked", async () => {
    const user = userEvent.setup();
    const { onChange } = renderFilters();

    await user.click(screen.getByRole("button", { name: /done/i }));

    expect(onChange).toHaveBeenCalledWith("done");
  });

  it("calls onChange exactly once per click", async () => {
    const user = userEvent.setup();
    const { onChange } = renderFilters();

    await user.click(screen.getByRole("button", { name: /done/i }));

    expect(onChange).toHaveBeenCalledTimes(1);
  });
});

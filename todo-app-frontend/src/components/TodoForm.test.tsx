import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TodoForm } from "./TodoForm";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderForm(onSubmit = vi.fn()) {
  render(<TodoForm onSubmit={onSubmit} />);
  return {
    titleInput: () => screen.getByPlaceholderText(/what needs to be done/i),
    descInput: () => screen.getByPlaceholderText(/description/i),
    prioritySelect: () => screen.getByRole("combobox"),
    submitBtn: () => screen.getByRole("button", { name: /add/i }),
    onSubmit,
  };
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe("TodoForm — rendering", () => {
  it("renders the form heading", () => {
    renderForm();
    expect(screen.getByRole("heading", { name: /new todo/i })).toBeInTheDocument();
  });

  it("renders a title input", () => {
    const { titleInput } = renderForm();
    expect(titleInput()).toBeInTheDocument();
  });

  it("renders a description textarea", () => {
    const { descInput } = renderForm();
    expect(descInput()).toBeInTheDocument();
  });

  it("renders a priority select defaulting to medium", () => {
    const { prioritySelect } = renderForm();
    expect((prioritySelect() as HTMLSelectElement).value).toBe("medium");
  });

  it("renders all three priority options", () => {
    renderForm();
    expect(screen.getByRole("option", { name: /low/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /medium/i })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /high/i })).toBeInTheDocument();
  });

  it("renders the Add button", () => {
    const { submitBtn } = renderForm();
    expect(submitBtn()).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Submission
// ---------------------------------------------------------------------------

describe("TodoForm — submission", () => {
  it("calls onSubmit with trimmed title and default priority", async () => {
    const user = userEvent.setup();
    const { titleInput, submitBtn, onSubmit } = renderForm();
    onSubmit.mockResolvedValue(undefined);

    await user.type(titleInput(), "  Buy groceries  ");
    await user.click(submitBtn());

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ title: "Buy groceries", priority: "medium" })
    );
  });

  it("calls onSubmit with selected priority", async () => {
    const user = userEvent.setup();
    const { titleInput, prioritySelect, submitBtn, onSubmit } = renderForm();
    onSubmit.mockResolvedValue(undefined);

    await user.type(titleInput(), "Task");
    await user.selectOptions(prioritySelect(), "high");
    await user.click(submitBtn());

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ priority: "high" })
    );
  });

  it("calls onSubmit with trimmed description", async () => {
    const user = userEvent.setup();
    const { titleInput, descInput, submitBtn, onSubmit } = renderForm();
    onSubmit.mockResolvedValue(undefined);

    await user.type(titleInput(), "Task");
    await user.type(descInput(), "  Some description  ");
    await user.click(submitBtn());

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ description: "Some description" })
    );
  });

  it("does NOT call onSubmit when title is blank", async () => {
    const user = userEvent.setup();
    const { submitBtn, onSubmit } = renderForm();

    await user.click(submitBtn());

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("resets fields after successful submission", async () => {
    const user = userEvent.setup();
    const { titleInput, descInput, prioritySelect, submitBtn, onSubmit } = renderForm();
    onSubmit.mockResolvedValue(undefined);

    await user.type(titleInput(), "Task");
    await user.type(descInput(), "desc");
    await user.selectOptions(prioritySelect(), "high");
    await user.click(submitBtn());

    expect((titleInput() as HTMLInputElement).value).toBe("");
    expect((descInput() as HTMLTextAreaElement).value).toBe("");
    expect((prioritySelect() as HTMLSelectElement).value).toBe("medium");
  });

  it("shows error message when onSubmit throws", async () => {
    const user = userEvent.setup();
    const { titleInput, submitBtn, onSubmit } = renderForm();
    onSubmit.mockRejectedValue(new Error("Server error"));

    await user.type(titleInput(), "Task");
    await user.click(submitBtn());

    expect(await screen.findByText(/server error/i)).toBeInTheDocument();
  });

  it("disables the button while submitting", async () => {
    const user = userEvent.setup();
    let resolve: () => void;
    const onSubmit = vi.fn(
      () => new Promise<void>((res) => { resolve = res; })
    );
    render(<TodoForm onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText(/what needs to be done/i), "T");
    const btn = screen.getByRole("button", { name: /add/i });

    user.click(btn); // fire and don't await

    // Button should be disabled immediately
    await vi.waitFor(() => expect(btn).toBeDisabled());

    resolve!();
  });
});

import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Dropzone } from "@/components/ui/dropzone";
import { toast } from "@/components/ui/toast";

vi.mock("@/components/ui/toast", () => ({
  toast: { error: vi.fn(), success: vi.fn(), warning: vi.fn(), info: vi.fn(), promise: vi.fn() },
}));

describe("Dropzone", () => {
  it("accepts valid files", () => {
    const onFiles = vi.fn();
    render(<Dropzone onFiles={onFiles} />);
    const input = screen.getByTestId("dropzone-input") as HTMLInputElement;

    const file = new File(["hello"], "terms.txt", { type: "text/plain" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(onFiles).toHaveBeenCalledWith([file]);
  });

  it("rejects unsupported file types", () => {
    const onFiles = vi.fn();
    render(<Dropzone onFiles={onFiles} />);
    const input = screen.getByTestId("dropzone-input") as HTMLInputElement;

    const file = new File(["hello"], "malware.exe", { type: "application/exe" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(onFiles).not.toHaveBeenCalled();
    expect(toast.error).toHaveBeenCalled();
  });

  it("shows selected files as chips", () => {
    const onFiles = vi.fn();
    render(<Dropzone onFiles={onFiles} />);
    const input = screen.getByTestId("dropzone-input") as HTMLInputElement;

    const file = new File(["hello"], "terms.pdf", { type: "application/pdf" });
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByTestId("dropzone-chip-name")).toBeInTheDocument();
  });
});

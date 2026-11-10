import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders default variant", () => {
    render(<Badge>LOW</Badge>);
    expect(screen.getByText("LOW")).toBeInTheDocument();
  });

  it("applies destructive variant", () => {
    render(<Badge variant="destructive">CRITICAL</Badge>);
    expect(screen.getByText("CRITICAL")).toHaveClass("bg-red-100");
  });
});

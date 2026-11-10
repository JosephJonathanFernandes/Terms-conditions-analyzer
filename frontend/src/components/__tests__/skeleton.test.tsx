import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Skeleton, SkeletonText, SkeletonCard } from "@/components/ui/skeleton";

describe("Skeleton", () => {
  it("renders text variant", () => {
    render(<Skeleton variant="text" />);
    expect(screen.getByTestId("skeleton-text")).toBeInTheDocument();
  });

  it("renders circular variant", () => {
    render(<Skeleton variant="circular" />);
    expect(screen.getByTestId("skeleton-circular")).toBeInTheDocument();
  });

  it("renders text group", () => {
    render(<SkeletonText count={3} />);
    expect(screen.getAllByTestId(/^skeleton-/)).toHaveLength(3);
  });

  it("renders card skeleton", () => {
    render(<SkeletonCard />);
    expect(screen.getAllByTestId("skeleton-text").length).toBeGreaterThan(0);
  });
});

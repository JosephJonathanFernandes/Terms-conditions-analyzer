import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RiskDistributionChart } from "@/components/charts/RiskDistributionChart";

describe("RiskDistributionChart", () => {
  it("renders with data", () => {
    render(<RiskDistributionChart distribution={{ LOW: 2, HIGH: 1, CRITICAL: 1 }} />);
    expect(screen.getByText("Risk Level Distribution")).toBeInTheDocument();
  });

  it("handles empty data gracefully", () => {
    render(<RiskDistributionChart distribution={{}} />);
    expect(screen.getByText("No risk data available")).toBeInTheDocument();
  });
});

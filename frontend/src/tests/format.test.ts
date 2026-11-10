import { describe, it, expect } from "vitest";
import { formatFileSize, riskColor, categoryLabel } from "@/utils/format";

describe("format utilities", () => {
  it("formatFileSize returns bytes for small values", () => {
    expect(formatFileSize(500)).toBe("500 B");
  });

  it("formatFileSize returns KB and MB", () => {
    expect(formatFileSize(2048)).toBe("2.0 KB");
    expect(formatFileSize(2 * 1024 * 1024)).toBe("2.00 MB");
  });

  it("riskColor returns classes for each level", () => {
    expect(riskColor("HIGH")).toContain("text-orange-700");
    expect(riskColor("CRITICAL")).toContain("text-red-700");
    expect(riskColor("LOW")).toContain("text-green-700");
    expect(riskColor(null)).toContain("text-gray-600");
  });

  it("categoryLabel title-cases", () => {
    expect(categoryLabel("third_party_data_sharing")).toBe("Third Party Data Sharing");
  });
});

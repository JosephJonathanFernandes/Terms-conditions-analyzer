export function formatFileSize(bytes: number | null): string {
  if (bytes == null) return "Unknown";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function formatDate(iso: string | null): string {
  if (!iso) return "Unknown";
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function riskColor(level: string | null | undefined): string {
  switch (level) {
    case "LOW": return "text-green-700 bg-green-100 border-green-200";
    case "MEDIUM": return "text-amber-700 bg-amber-100 border-amber-200";
    case "HIGH": return "text-orange-700 bg-orange-100 border-orange-200";
    case "CRITICAL": return "text-red-700 bg-red-100 border-red-200";
    default: return "text-gray-600 bg-gray-100 border-gray-200";
  }
}

export function categoryLabel(category: string): string {
  return category
    .split(/_|-|\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

export function truncateText(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen).trim() + "…";
}

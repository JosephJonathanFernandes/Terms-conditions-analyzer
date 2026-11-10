import type {
  IngestResponse,
  Analysis,
  ChatResponse,
  ComparisonResponse,
  HistoryItem,
  DocumentListItem,
} from "@/types";

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

class ApiError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

async function request<T>(
  input: string,
  init?: RequestInit
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(`${API_BASE}${input}`, {
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
      ...init,
    });

    if (!res.ok) {
      let detail = `Request failed (${res.status})`;
      let code = "error";
      try {
        const body = await res.json();
        detail = body.error?.message || body.detail || detail;
        code = body.error?.code || code;
      } catch {
        // ignore
      }
      throw new ApiError(res.status, code, detail);
    }

    if (res.status === 204) return undefined as T;
    return res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  ingestUrl: (url: string) =>
    request<IngestResponse>("/ingest/url", {
      method: "POST",
      body: JSON.stringify({ url }),
    }),

  ingestFile: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<IngestResponse>("/ingest/file", {
      method: "POST",
      body: form,
      headers: {},
    });
  },

  ingestText: (text: string) =>
    request<IngestResponse>("/ingest/text", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),

  analyze: (documentId: number, explanationLevel: "simple" | "standard" | "detailed" = "standard") =>
    request<Analysis>("/analyze", {
      method: "POST",
      body: JSON.stringify({ document_id: documentId, explanation_level: explanationLevel }),
    }),

  getAnalysis: (analysisId: number) =>
    request<Analysis>(`/analysis/${analysisId}`),

  chat: (analysisId: number, question: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ analysis_id: analysisId, question }),
    }),

  compare: (analysisIdA: number, analysisIdB: number) =>
    request<ComparisonResponse>("/compare", {
      method: "POST",
      body: JSON.stringify({ analysis_id_a: analysisIdA, analysis_id_b: analysisIdB }),
    }),

  history: () => request<HistoryItem[]>("/history"),

  deleteAnalysis: (analysisId: number) =>
    request<{ ok: boolean }>(`/history/${analysisId}`, {
      method: "DELETE",
    }),

  listDocuments: (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    source_type?: string;
  }) => {
    const qs = new URLSearchParams();
    if (params?.page) qs.set("page", String(params.page));
    if (params?.page_size) qs.set("page_size", String(params.page_size));
    if (params?.status) qs.set("status", params.status);
    if (params?.source_type) qs.set("source_type", params.source_type);
    return request<{
      items: DocumentListItem[];
      total: number;
      page: number;
      page_size: number;
      pages: number;
    }>(`/documents?${qs.toString()}`);
  },

  deleteDocument: (documentId: number) =>
    request<{ ok: boolean }>(`/documents/${documentId}`, {
      method: "DELETE",
    }),

  exportDocument: (documentId: number, format: "txt" | "json" | "pdf" = "json") =>
    fetch(`${API_BASE}/documents/${documentId}/export?format=${format}`),
};

export type { ApiError };

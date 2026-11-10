# ClauseClear — System Architecture

## 1. Overview

ClauseClear is a full-stack web application that helps ordinary users understand Terms & Conditions, Privacy Policies, and other legal documents before accepting them.

**Guiding design decision:** Build a deterministic clause-detection and evidence-extraction engine first, then use an LLM to explain findings. Do not make an LLM responsible for everything. This makes the system testable, explainable, and technically defensible.

**Stack priorities:** Simplicity, maintainability, CPU-friendly execution, no mandatory paid dependencies, local development supported on an 8 GB RAM i5 laptop.

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                │
│  Landing | Analysis | Results | Q&A | Compare | History     │
│  Documents                                                       │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTPS/JSON (CORS-restricted, rate-limited)
┌──────────────────▼──────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  /api/ingest   /api/analyze   /api/chat                     │
│  /api/compare  /api/history   /api/documents                │
│  /api/report   /api/export                                  │
└──────────────┬───────────┬───────────┬─────────────────────┘
               │           │           │
    ┌──────────▼──┐ ┌──────▼──────┐ ┌─▼─────────────┐
    │ Ingestion   │ │ Analysis    │ │ RAG / Q&A     │
    │ Service     │ │ Engine      │ │ Service       │
    └──────────┬──┘ └──────┬──────┘ └───────┬────────┘
               │           │                │
    ┌──────────▼──┐ ┌──────▼──────┐ ┌──────▼───────┐
    │ URL / PDF   │ │ Clause      │ │ TF-IDF       │
    │ DOCX / TXT  │ │ Detection   │ │ Retrieval    │
    │ Text        │ │ Classification│ │ LLM Explain  │
    └──────────┬──┘ └──────┬──────┘ └──────┬───────┘
               │           │                │
    ┌──────────▼──┐ ┌──────▼──────┐ ┌──────▼───────┐
    │ Security:   │ │ Risk Engine │ │ Evidence     │
    │ SSRF guard, │ │ (rule-based)│ │ Store        │
    │ file scan,  │ │             │ │              │
    │ sanitization│ └─────────────┘ └──────────────┘
    └──────────┬──┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │                      SQLite                           │
    │  documents, analyses, clauses, analysis_history      │
    │  (PostgreSQL-swappable via DATABASE_URL)             │
    └──────────────────────────────────────────────────────┘
```

## 3. Middleware Stack

| Order | Middleware | Purpose |
|-------|-----------|---------|
| 1 | CORS | Restricted origins |
| 2 | Rate Limiting | Per-IP fixed-window limits |
| 3 | Error Handling | Consistent JSON errors, no stack traces, X-Request-ID |

## 4. Layer Responsibilities

### Frontend (React + TypeScript + Vite + Tailwind)
- Pages: Landing, Analysis, Results Dashboard, Ask Your Terms (Q&A), Compare Documents, History, Documents, Clause Detail
- State management: React Query (server state), React hooks (local state)
- UI: Tailwind CSS, Lucide icons, Recharts charts, Sonner toasts, Framer Motion
- Accessibility: ARIA labels, focus management, prefers-reduced-motion

### Backend (FastAPI + Python)
- `api/` — route handlers (ingestion, analysis, chat, comparison, history, documents, report, health)
- `services/` — business logic (ingestion, extraction, clause_detection, risk_engine, simplification, llm_provider, rag, comparison, export, report)
- `middleware/` — error handling, rate limiting
- `models/` — SQLAlchemy models (document, clause, analysis)
- `schemas/` — Pydantic request/response schemas
- `database/` — SQLite engine/session, PostgreSQL-swappable
- `security/` — SSRF guard, file validation, filename sanitization, HTML sanitization
- `utils/` — logging, config, text helpers

### Data Flow

1. User submits URL / file / text
2. Backend validates input (SSRF checks, file type/size, filename sanitization)
3. Rate limit check per client IP
4. Extraction service extracts raw text + metadata (PyMuPDF, python-docx, Trafilatura, BeautifulSoup)
5. Text is cleaned (duplicate removal, HTML cleanup, truncation)
6. Document stored in SQLite with content hash for deduplication
7. Clause detection engine segments text into clauses and classifies into 21 categories (rule-based baseline)
8. Risk engine assigns LOW/MEDIUM/HIGH/CRITICAL with rationale + evidence
9. Optional LLM (OpenAI-compatible or Ollama) simplifies clauses; rule-based fallback when no LLM
10. RAG service indexes chunks for Q&A with TF-IDF retrieval
11. Results stored in SQLite; report generated; PDF/TXT/JSON export available

## 5. Data Models (SQLite, PostgreSQL-ready)

- **Document**: id, filename, source_type, source_url, content_hash, file_size, mime_type, extracted_text, metadata_json, status, failure_reason, page_count, language, extraction_warnings_json, downloaded_at, uploaded_at, retention_delete_at
- **Analysis**: id, document_id, status, summary, risk_distribution_json, explanation_level, llm_mode, created_at
- **Clause**: id, analysis_id, category, original_text, simplified_text, risk_level, risk_rationale, confidence, source_location, paragraph_index, evidence_json, suggested_questions_json, created_at

## 6. AI Provider Abstraction

- `BaseLLMProvider` — interface
- `NoneProvider` — rule-based fallback (default)
- `OllamaProvider` — local Ollama
- `OpenAICompatibleProvider` — OpenAI-compatible API

Two modes: AI-assisted (LLM) and rule-based fallback (no LLM configured). Structured JSON outputs with schema validation. System instructions are separated from document content to resist prompt injection.

## 7. Security Boundaries

- SSRF protection: block localhost, private IP ranges (RFC 1918), link-local, cloud metadata endpoints; validate redirects; DNS/IP checks; timeouts and size limits
- File validation: extension + magic-byte content verification, size limits, filename sanitization, safe temp-file handling, no execution of uploaded files
- HTML sanitization on extracted content
- Rate limiting, CORS configuration, secure error handling (no stack traces to client)
- Secrets via environment variables only; `.env.example` provided, no hardcoded keys
- Document retention policy with explicit deletion

## 8. Testing

- Backend: pytest (70 tests covering API, extraction, detection, risk, documents, rate limiting, errors)
- Frontend: Vitest + React Testing Library (19 component tests)
- E2E: Playwright (ingestion, history, compare, accessibility)

## 9. Phased Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Project setup, frontend+backend init, SQLite, landing page, health check | Complete |
| 2 | Ingestion (PDF/DOCX/TXT/text/URL), validation & security | Complete |
| 3 | Analysis engine (clause detection, classification, simplification, risk) | Complete |
| 4 | Results dashboard, risk indicators, side-by-side view, PDF export | Complete |
| 5 | RAG chunking/retrieval, document-grounded Q&A, citations | Complete |
| 6 | Document comparison, history, document management, export | Complete |
| 7 | Production hardening (error middleware, rate limiting, tests, docs, deployment) | Complete |

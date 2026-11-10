# ClauseClear — Development Roadmap

## Phase 1: Project Setup — Complete
- Initialize backend (FastAPI, SQLAlchemy, SQLite) and frontend (React, Vite, TypeScript, Tailwind)
- Configure `.env.example`, `requirements.txt`, `package.json`
- Base SQLAlchemy models + session management
- Landing page with input method selection (URL / upload / paste text)
- API health check `GET /api/health`
- Verify: uvicorn runs backend, vite runs frontend, health check returns 200

## Phase 2: Ingestion — Complete
- PDF extraction (PyMuPDF), DOCX (python-docx), TXT
- Website extraction (Trafilatura + BeautifulSoup), fallback
- URL validation, SSRF guards, redirect/DNS checks, timeouts, size limits
- robots.txt respect, legal-page discovery
- File validation, size limits, filename sanitization, duplicate text removal, metadata extraction

## Phase 3: Analysis Engine — Complete
- Clause segmentation into 21 categories (rule-based baseline)
- Classification service, simplification service (3 levels: Simple/Standard/Detailed)
- Risk engine: LOW/MEDIUM/HIGH/CRITICAL with rationale + evidence
- LLM provider abstraction (OpenAI-compatible, Ollama) + rule-based fallback

## Phase 4: Results Dashboard — Complete
- Executive summary, key obligations, user rights, data collection, financial commitments
- Risk distribution bar + pie charts, clause category distribution bar chart
- Original vs simplified clause table, row click to clause detail
- PDF/TXT/JSON document export

## Phase 5: RAG and Q&A — Complete
- TF-IDF retrieval over document clauses
- Document-grounded Q&A with citations, source location references
- "Document does not specify" handling; no fabrication

## Phase 6: Advanced Features — Complete
- Document comparison (added/removed/modified clauses, impact analysis)
- History (view, reopen, delete)
- Document management (list, delete, export all)
- Document export (TXT, JSON, PDF, ZIP bulk export)

## Phase 7: Production Hardening — Complete
- Global error handling middleware (consistent JSON errors, no stack traces, X-Request-ID)
- Rate limiting middleware (per-IP fixed-window, 429 with Retry-After)
- Document CRUD router (list, get, delete, export)
- Failure status for failed extractions (no unhandled exceptions)
- Content-hash deduplication short-circuit
- 70 backend pytest tests, 19 frontend Vitest tests
- Playwright E2E test suite (4 test files)
- Deployment guide, testing guide, user guide, API docs
- `.env.example` for backend and frontend
- Docker deployment guidance

## Phase 8: Future Enhancements (Backlog)
- Alembic migrations for schema versioning
- Multi-worker Redis-backed rate limiting
- OAuth / user authentication
- Multi-language support
- OCR for scanned PDFs
- Scheduled retention sweep CLI
- Prometheus metrics endpoint
- Code-splitting for large frontend bundle

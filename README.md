# ClauseClear

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vitejs.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 70 backend + 19 frontend](https://img.shields.io/badge/tests-89-green.svg)](./backend/tests/)
[![SQLite](https://img.shields.io/badge/database-SQLite-blue.svg)](https://sqlite.org)

## 📖 About

**ClauseClear** is an AI-powered Terms & Conditions analyzer that helps ordinary users understand what they're agreeing to before accepting legal documents. It extracts text from website URLs, PDFs, DOCX files, or pasted text; detects 21 legal clause categories; assigns explainable risk levels (LOW/MEDIUM/HIGH/CRITICAL); simplifies complex legal language into plain English; and answers document-grounded questions with source citations.

> ⚠️ **Not legal advice.** ClauseClear provides informational explanations only. Consult a qualified attorney for legal interpretation.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **🔗 URL Ingestion** | Enter a website URL to discover and extract its Terms & Conditions / Privacy Policy |
| **📄 File Upload** | Upload PDF, DOCX, or TXT files (max 25 MB each) |
| **🔍 OCR for Scanned PDFs** | Tesseract-powered OCR extracts text from image-based PDFs (optional, requires Tesseract installed) |
| **📝 Text Input** | Paste legal text directly into the editor |
| **🔍 Clause Detection** | 21 legal categories (data sharing, arbitration, liability, renewal, etc.) |
| **⚠️ Risk Engine** | LOW / MEDIUM / HIGH / CRITICAL with explainable rationale and evidence |
| **💬 Simplification** | Simple / Standard / Detailed explanation levels |
| **🤖 Ask Your Terms** | RAG-powered Q&A with citations to original clauses |
| **📊 Results Dashboard** | Risk distribution charts, clause category breakdown, executive summary |
| **🔄 Document Comparison** | Compare two versions — see added, removed, and modified clauses |
| **📥 Export** | Download analysis as PDF, JSON, or TXT |
| **🗂️ History** | View, reopen, delete, and export previous analyses |
| **🔒 Security** | SSRF protection, file magic-byte validation, HTML sanitization, prompt-injection guards |
| **⚡ CPU-Friendly** | Rule-based by default — works offline, no GPU, no paid API required |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (tested on 3.14)
- **Node.js 18+** (tested on 20)
- **8 GB RAM** recommended; CPU-only (no GPU required)

### One-Command Setup (Windows)

```powershell
.\install.bat
```

### One-Command Setup (macOS / Linux)

```bash
chmod +x install.sh
./install.sh
```

### Manual Setup

**Backend:**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# OR: source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # Windows
# OR: cp .env.example .env      # macOS/Linux
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Frontend:**
```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. The backend health check is at **http://127.0.0.1:8000/health**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React + Vite)                │
│  Landing | Analysis | Results | Q&A | Compare | History     │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTPS/JSON (CORS-restricted, rate-limited)
┌──────────────────▼──────────────────────────────────────────┐
│                    Backend (FastAPI + SQLAlchemy)           │
│  /api/ingest   /api/analyze   /api/chat                     │
│  /api/compare  /api/history   /api/documents                │
│  /api/export   /api/report    /health                       │
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
    │  documents, analyses, clauses (PostgreSQL-swappable)  │
    └──────────────────────────────────────────────────────┘
```

### AI Modes

| Mode | Description | LLM Required |
|------|-------------|--------------|
| **Rule-based** (default) | Deterministic detection, risk, simplification | ❌ No |
| **AI-assisted** | LLM-powered explanations via Ollama or OpenAI-compatible API | ✅ Optional |

Set `LLM_PROVIDER=ollama` or `openai-compatible` in `.env` to enable AI-assisted mode.

---

## 🧪 Testing

### Backend (70 tests)

```powershell
cd backend
python -m pytest tests/ -q
```

### Frontend (19 tests)

```powershell
cd frontend
npm test
```

### End-to-End (Playwright)

```powershell
cd frontend
npm run test:e2e
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Reference](./docs/api.md) | Complete REST API documentation |
| [Architecture](./docs/architecture.md) | System design and data flow |
| [Deployment](./docs/deployment.md) | Production deployment guide |
| [Testing](./docs/testing.md) | How to run all test suites |
| [User Guide](./docs/user-guide.md) | End-user how-to |
| [Threat Model](./docs/threat-model.md) | Security threat analysis |
| [Roadmap](./docs/development-roadmap.md) | Release phases and backlog |

---

## 🔒 Security

ClauseClear treats all extracted website and document content as **untrusted data**:

- **SSRF Protection** — blocks localhost, private IP ranges (RFC 1918), cloud metadata endpoints, and validates redirects
- **File Validation** — extension + magic-byte verification, size limits, filename sanitization
- **HTML Sanitization** — strips scripts, styles, iframes, and dangerous attributes
- **Prompt Injection Guards** — system instructions separated from document content
- **Secure Error Handling** — no stack traces leaked to clients
- **Secrets via Environment Variables** — no hardcoded API keys

See [`docs/threat-model.md`](./docs/threat-model.md) for the full threat model.

---

## 🤝 Contributing

Contributions are welcome! Please read the contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "feat: add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Development Rules

- Build one phase at a time; ensure each phase runs before proceeding
- Use clean, modular, typed, maintainable code
- Avoid unnecessary abstractions and dependencies
- Do not use paid services as mandatory dependencies
- Support CPU-only local development
- Never use mock analysis results in the final application
- If an external LLM is unavailable, clearly identify rule-based results

---

## 📜 License

This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com) — Backend framework
- [React](https://react.dev) — Frontend library
- [Vite](https://vitejs.dev) — Build tool
- [Tailwind CSS](https://tailwindcss.com) — Styling
- [Recharts](https://recharts.org) — Data visualization
- [PyMuPDF](https://pymupdf.readthedocs.io) — PDF extraction
- [python-docx](https://python-docx.readthedocs.io) — DOCX extraction
- [Trafilatura](https://trafilatura.readthedocs.io) — Web extraction
- [Sonner](https://sonner.emilkowal.ski) — Toast notifications
- [TanStack Query](https://tanstack.com/query) — Server state

---

<div align="center">
  <b>ClauseClear</b> — Understand what you're agreeing to.
  <br><br>
  <sub>⚠️ Informational explanations only — not legal advice.</sub>
</div>

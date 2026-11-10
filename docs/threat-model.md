# ClauseClear — Threat Model

## 1. Threats and Mitigations

| Threat | Asset | Mitigation |
|--------|-------|------------|
| SSRF via website URL input | Backend, internal network | Validate URL schemes; block localhost, private IPs (RFC 1918), link-local, cloud metadata endpoints (169.254.169.254); validate redirects; DNS resolution check; request timeout + size limit |
| Malicious file upload | Backend, host | Extension + magic-byte verification, size limit, filename sanitization, store outside web root, never execute uploaded files, scan temp files, delete after processing |
| Prompt injection via document content | LLM outputs, analysis integrity | Treat extracted text as untrusted; system instructions separated from user content; no document-provided instructions override system behavior; sanitize LLM outputs |
| XSS via extracted HTML | Frontend users | HTML sanitization before rendering; never `dangerouslySetInnerHTML` with raw content; encode outputs |
| Hardcoded secrets | Credentials | Environment-variable-based secrets only; `.env.example` with placeholders; no keys in code |
| Information leakage in errors | Attackers | Generic client error messages; server-side logging only; no stack traces to client |
| Unauthorized cross-origin access | API | CORS configured to allowed origins only |
| Brute force / abuse | API | Rate limiting on ingestion and analysis endpoints |
| Indefinite document storage | User data | Explicit retention policy; user-triggered deletion; `retention_delete_at` on documents |

## 2. Out of Scope

- Legal advice: the app provides informational explanations only; a disclaimer is shown on every results page
- Authentication/authorization: Phase 1–7 use anonymous session-based history; no user accounts

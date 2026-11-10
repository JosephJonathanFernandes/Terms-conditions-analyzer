# ClauseClear — API Reference

Base path: `/api`

## Authentication

ClauseClear currently operates without user authentication. All endpoints are accessible to any caller. Rate limits are applied per client IP.

## Error Responses

All errors return a consistent JSON shape:

```json
{
  "error": {
    "code": "bad_request",
    "message": "Human-readable message",
    "request_id": "uuid"
  }
}
```

Common error codes:
- `bad_request` (400)
- `not_found` (404)
- `conflict` (409)
- `validation_error` (422)
- `rate_limited` (429)
- `internal_error` (500)

Every response includes an `X-Request-ID` header for tracing.

## Rate Limiting

Rate limits are applied per client IP. Response headers include:
- `X-RateLimit-Limit`: Requests allowed per minute
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Seconds until window resets
- `Retry-After`: Seconds to wait (on 429 responses)

| Endpoint | Limit (req/min) |
|----------|-----------------|
| `GET /health` | 60 |
| `POST /api/ingest/*` | 10 |
| `POST /api/analyze` | 10 |
| `POST /api/chat` | 20 |
| All other endpoints | 60 |

## Endpoints

### Health

`GET /health`

Returns service status and LLM mode.

### Ingestion

`POST /api/ingest/url`

Body: `{ "url": "https://example.com/terms" }`

Validates the URL (SSRF protection), extracts text, and stores the document.

`POST /api/ingest/file`

Form: `file` (PDF, DOCX, TXT; max 25 MB)

Validates file type (extension + magic bytes), extracts text, stores the document.

`POST /api/ingest/text`

Body: `{ "text": "..." }` (form-encoded)

Stores pasted text as a document.

Response (all ingest endpoints):

```json
{
  "document_id": 1,
  "status": "extracted",
  "extracted_length": 1234,
  "source_type": "text",
  "discovered_documents": null,
  "message": "Text ingested successfully."
}
```

### Analysis

`POST /api/analyze`

Body: `{ "document_id": 1, "explanation_level": "standard" }`

Runs clause detection, risk assessment, and simplification. Returns the full analysis with clauses.

`GET /api/analysis/{id}`

Returns the stored analysis result.

### Document Management

`GET /api/documents`

Query params: `page`, `page_size`, `status`, `source_type`

Returns paginated document list.

`GET /api/documents/{id}`

Returns document metadata.

`DELETE /api/documents/{id}`

Deletes a document and its analysis. Returns 204.

`GET /api/documents/{id}/export?format=txt\|json\|pdf`

Exports a single document as a file download.

`GET /api/documents/export/all?format=txt\|json\|pdf`

Exports all documents as a ZIP archive.

### Q&A (RAG)

`POST /api/chat`

Body: `{ "analysis_id": 1, "question": "Can they share my data?" }`

Returns a grounded answer with citations:

```json
{
  "answer": "Based on the document...",
  "citations": [
    {
      "clause_id": 5,
      "category": "third_party_data_sharing",
      "source_location": "Paragraph 3",
      "quote": "We share your data with third parties."
    }
  ],
  "document_does_not_specify": false
}
```

### Comparison

`POST /api/compare`

Body: `{ "analysis_id_a": 1, "analysis_id_b": 2 }`

Returns added, removed, and modified clauses with impact summaries.

### History

`GET /api/history`

Returns a list of previous analyses.

`DELETE /api/history/{id}`

Deletes an analysis record.

### Report

`GET /api/report/{id}/pdf`

Downloads a PDF report of the analysis.

## OpenAPI Docs

Interactive API documentation is available at `GET /docs` when the server is running.

# ClauseClear — Testing Guide

## Backend Tests (pytest)

### Run all backend tests

```bash
cd backend
python -m pytest tests/ -q
```

### Run with coverage

```bash
cd backend
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### Test files

| File | What it tests |
|------|---------------|
| `test_api_ingest.py` | Health, text ingestion, SSRF blocking |
| `test_documents.py` | Document CRUD, export (txt/json/pdf), pagination, duplicates |
| `test_extraction_pdf.py` | PDF text extraction, scanned PDF detection |
| `test_extraction_docx.py` | DOCX extraction, tables, metadata |
| `test_extraction_txt.py` | TXT extraction |
| `test_clause_detection.py` | All 21 clause categories |
| `test_risk_engine.py` | Risk levels, escalation/de-escalation, distribution |
| `test_rate_limiting.py` | Rate limiter window logic |
| `test_error_middleware.py` | Error response shapes, request IDs |

### Coverage target

≥ 85% coverage on `app/services` and `app/security`.

## Frontend Tests (Vitest + React Testing Library)

### Run all frontend tests

```bash
cd frontend
npm test
```

### Test files

| File | What it tests |
|------|---------------|
| `src/tests/format.test.ts` | Formatting utilities |
| `src/components/__tests__/button.test.tsx` | Button component |
| `src/components/__tests__/badge.test.tsx` | Badge component |
| `src/components/__tests__/skeleton.test.tsx` | Skeleton loading states |
| `src/components/__tests__/dropzone.test.tsx` | Drag-and-drop upload |
| `src/components/__tests__/risk-distribution-chart.test.tsx` | Recharts charts |

### Run UI mode

```bash
cd frontend
npx vitest
```

## End-to-End Tests (Playwright)

### Install browsers (first time only)

```bash
cd frontend
npx playwright install
```

### Run E2E tests

```bash
cd frontend
npm run test:e2e
```

### E2E test files

| File | What it tests |
|------|---------------|
| `e2e/tests/ingest.spec.ts` | Text ingestion → results, SSRF blocking |
| `e2e/tests/history.spec.ts` | History page |
| `e2e/tests/compare.spec.ts` | Compare page |
| `e2e/tests/a11y.spec.ts` | Accessibility basics |

### Run specific project

```bash
npm run test:e2e -- --project=chromium
npm run test:e2e -- --project=mobile
```

### UI mode

```bash
npm run test:e2e:ui
```

## Continuous Integration

A sample GitHub Actions workflow would:

1. Lint backend (`ruff check backend/`) and frontend (`npm run lint`)
2. Run backend tests with coverage
3. Run frontend unit tests
4. Install Playwright browsers and run E2E tests against dev servers
5. Build frontend (`npm run build`) to verify no compile errors

## Writing New Tests

### Backend

- Place tests in `backend/tests/`
- Use the `client` fixture from `conftest.py`
- Use the `clean_db` fixture for tests that create documents
- Follow the existing AAA (Arrange-Act-Assert) pattern

### Frontend

- Place component tests in `src/components/__tests__/`
- Use `@testing-library/react` with `vitest`
- Mock `sonner` toast and `api` service as needed

# ClauseClear — Deployment Guide

## Production Deployment Options

### Option 1: Docker (Recommended)

Build and run with Docker Compose:

```bash
# From the clauseclear directory
docker-compose up --build
```

This starts:
- Backend (FastAPI + uvicorn) on port 8000
- Frontend (Vite dev server, or served static files) on port 5173

#### `docker-compose.yml`

Create this at the repo root:

```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend/clauseclear.db:/app/clauseclear.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
    restart: unless-stopped
```

#### `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 2: Manual (Bare Metal)

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your production values
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_BASE=http://your-backend:8000/api
npm run build
npm run preview   # or serve dist/ with nginx/Caddy
```

### Environment Variables

#### Backend (`backend/.env`)

| Variable | Description | Default | Required in Prod |
|----------|-------------|---------|------------------|
| `APP_ENV` | `development` \| `production` | `development` | Yes |
| `SECRET_KEY` | Random string for sessions | `change-me-in-production` | **Yes** |
| `DEBUG` | Enable debug mode | `false` | No |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` | Yes |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./clauseclear.db` | No |
| `LLM_PROVIDER` | `none` \| `ollama` \| `openai-compatible` | `none` | No |
| `OPENAI_API_KEY` | OpenAI-compatible API key | `` | No (if using LLM) |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size in MB | `25` | No |
| `DOCUMENT_RETENTION_DAYS` | Days before auto-deletion | `30` | No |

#### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE` | Backend API base URL | `http://127.0.0.1:8000/api` |

### Reverse Proxy (nginx)

Example nginx config for production:

```nginx
server {
    listen 80;
    server_name clauseclear.example.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 25M;
    }

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
    }
}
```

### Database Migration (SQLite → PostgreSQL)

ClauseClear uses SQLAlchemy, so switching databases is straightforward:

1. Set `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname`
2. Install `psycopg2-binary`: `pip install psycopg2-binary`
3. Run `alembic upgrade head` to create tables
4. The existing `create_all()` on startup will also work for fresh databases

### Security Checklist

- [ ] Change `SECRET_KEY` from the default
- [ ] Set `APP_ENV=production`
- [ ] Disable `DEBUG`
- [ ] Restrict `CORS_ORIGINS` to your domain(s)
- [ ] Use HTTPS (TLS termination at reverse proxy)
- [ ] Set `DATABASE_URL` to PostgreSQL for production workloads
- [ ] Configure rate limits appropriately for your traffic
- [ ] Set up document retention (`DOCUMENT_RETENTION_DAYS`)

### Monitoring

- Health check: `GET /health`
- API docs: `GET /docs`
- Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Request tracing: `X-Request-ID` header on all responses

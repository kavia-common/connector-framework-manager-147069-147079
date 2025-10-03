# Integration Steps: core_backend + core_frontend

This guide summarizes the steps to integrate and validate the FastAPI backend with the Next.js frontend.

1) Environment variables
- core_backend/.env (copy from .env.example):
  - DATABASE_URL=<postgres or sqlite url>
  - BACKEND_BASE_URL=http://localhost:3001
  - FRONTEND_BASE_URL=http://localhost:3000
  - JWT_SECRET=<secure string>
  - OAUTH_REDIRECT_BASE=${FRONTEND_BASE_URL}
  - Optional per-connector client IDs/secrets
- core_frontend/.env.local (copy from .env.local.example):
  - NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:3001
  - NEXT_PUBLIC_FRONTEND_BASE_URL=http://localhost:3000
  - Optional NEXT_PUBLIC_* client IDs/secrets

2) Apply migrations
- cd core_backend
- Use the helper script:
  - bash utils/run_migrations.sh
  - If you see “index already exists” with SQLite, reset then re-run:
    - bash utils/run_migrations.sh reset

3) Start services
- Backend (port 3001):
  - . venv/bin/activate && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
- Frontend (port 3000):
  - cd core_frontend && npm install && npm run dev

4) CORS
- Backend allows both FRONTEND_BASE_URL and BACKEND_BASE_URL
- Ensure values match your running URLs exactly

5) OpenAPI specification sync
- cd core_backend && . venv/bin/activate && python -m src.api.generate_openapi
- Copy core_backend/interfaces/openapi.json contents into core_frontend/backend-api-spec.json (already updated in repo)

6) OAuth dry-run (simulation)
- Initiate:
  - GET {BACKEND_BASE_URL}/api/oauth/{connector}/authorize[?connection_id=ID]
  - Returns { authorization_url, state }
- Callback:
  - POST {BACKEND_BASE_URL}/api/oauth/{connector}/callback with { code: "dev-code", state, connection_id?: ID }
- Verify:
  - Response success === true
  - If a connection_id is provided and plugin supports it in dev, connection status becomes "active"

7) Provider redirect URIs
- Configure providers to use:
  - {FRONTEND_BASE_URL}/oauth/callback

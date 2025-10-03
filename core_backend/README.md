# Connector Framework Manager - Backend

Main backend server providing the core API for connectors, authentication, plugin management, and service orchestration.

## Overview

This FastAPI-based backend provides:
- REST API endpoints for connector management
- OAuth integration for third-party services
- Plugin loading system for connectors
- Database models for users, connectors, and connections
- JWT-based authentication
- OpenAPI generation for sharing with frontend

## Environment Setup

### 1. Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/connector_framework_db
# or for local development:
# DATABASE_URL=sqlite:///./connector_framework.db

# Application Configuration
APP_NAME=Connector Framework Manager
JWT_SECRET=your-super-secret-jwt-key-here-minimum-32-characters
BACKEND_BASE_URL=http://localhost:3001
FRONTEND_BASE_URL=http://localhost:3000

# OAuth Client IDs and Secrets (configure for each connector you plan to use)
JIRA_CLIENT_ID=your-jira-client-id
JIRA_CLIENT_SECRET=your-jira-client-secret
CONFLUENCE_CLIENT_ID=your-confluence-client-id
CONFLUENCE_CLIENT_SECRET=your-confluence-client-secret
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
NOTION_CLIENT_ID=your-notion-client-id
NOTION_CLIENT_SECRET=your-notion-client-secret
FIGMA_CLIENT_ID=your-figma-client-id
FIGMA_CLIENT_SECRET=your-figma-client-secret
DATADOG_CLIENT_ID=your-datadog-client-id
DATADOG_CLIENT_SECRET=your-datadog-client-secret
```

### 2. OAuth Configuration

For each connector you want to use, you'll need to:

1. Register your application with the third-party service.
2. Set the redirect URI to: `http://localhost:3000/oauth/callback` (FRONTEND_BASE_URL + `/oauth/callback`).
3. Configure the client ID and secret in your `.env` file.

State parameter is a signed token with expiry to prevent CSRF.

#### Connector-specific OAuth Setup:

- Jira/Confluence: Atlassian Developer Console
- Slack: Slack API portal
- Notion: Notion Developers
- Figma: Figma Developers
- Datadog: Datadog App Management

## Database and Migrations

- JSON fields are JSONB on PostgreSQL and JSON on SQLite.
- Unique constraints and FKs:
  - connectors.key unique
  - users.email unique
  - connections unique (user_id, connector_id) with ON DELETE CASCADE

Run migrations:

```bash
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

Troubleshooting:
- If using the default SQLite file and you re-run migrations, you may see:
  - sqlite3.OperationalError: index ix_users_email already exists
- Fix by removing the local SQLite DB file or switching to a fresh database, then re-running `alembic upgrade head`.

## Development

### Prerequisites

- Python 3.8+
- PostgreSQL database (recommended)
- Virtual environment (recommended)

### Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

### Running the Server

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
```

Endpoints:
- API: http://localhost:3001/api
- Swagger: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc
- OpenAPI: http://localhost:3001/openapi.json
- Health: http://localhost:3001/healthz and http://localhost:3001/readyz

## API Endpoints

### Connectors
- GET `/api/connectors/` - List all available connectors
- GET `/api/connectors/{key}` - Get connector details
- POST `/api/connectors/` - Create custom connector
- PUT `/api/connectors/{key}` - Update connector
- DELETE `/api/connectors/{key}` - Delete connector

### Connections
- GET `/api/connections/` - List user connections
- POST `/api/connections/` - Create new connection
- GET `/api/connections/{id}` - Get connection details
- PUT `/api/connections/{id}` - Update connection
- DELETE `/api/connections/{id}` - Delete connection
- POST `/api/connections/{id}/test` - Test connection

### OAuth
- GET `/api/oauth/{connector}/authorize` - Initiate OAuth flow (returns authorization_url and signed state)
- GET `/api/oauth/{connector}/callback` - Handle OAuth callback (GET)
- POST `/api/oauth/{connector}/callback` - Handle OAuth callback (POST)
- DELETE `/api/oauth/{connector}/revoke/{connection_id}` - Revoke OAuth token

### Health
- GET `/healthz` - Liveness probe
- GET `/readyz` - Readiness probe

## CORS

Configured to allow:
- FRONTEND_BASE_URL
- BACKEND_BASE_URL

No wildcard origins used.

## OpenAPI Generation

Export OpenAPI to interfaces/openapi.json:

```bash
python -m src.api.generate_openapi
```

Commit the updated file to keep the frontend in sync.

## Production Deployment

- Set secure environment variables
- Use a production ASGI server (e.g., Gunicorn + Uvicorn workers)
- Configure HTTPS, logging, and monitoring

Example:

```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
```

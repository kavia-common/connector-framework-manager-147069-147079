# Connector Framework Manager - Backend

Main backend server providing the core API for connectors, authentication, plugin management, and service orchestration.

## Overview

This FastAPI-based backend provides:
- REST API endpoints for connector management
- OAuth integration for third-party services
- Plugin loading system for connectors
- Database models for users, connectors, and connections
- JWT-based authentication

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

1. **Register your application** with the third-party service
2. **Set the redirect URI** to: `http://localhost:3000/oauth/callback`
3. **Configure the client ID and secret** in your `.env` file

#### Connector-specific OAuth Setup:

- **Jira/Confluence**: Create an OAuth 2.0 app in Atlassian Developer Console
- **Slack**: Create a Slack app in the Slack API portal
- **Notion**: Create an integration in Notion Developers
- **Figma**: Create an app in Figma Developers
- **Datadog**: Create an OAuth app in Datadog App Management

## Development

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up database:**
```bash
# Run database migrations
alembic upgrade head
```

### Running the Server

Start the development server:

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 3001
```

The API will be available at:
- **API Endpoints**: http://localhost:3001/api
- **Interactive Docs**: http://localhost:3001/docs
- **OpenAPI Schema**: http://localhost:3001/openapi.json

### API Documentation

The backend provides comprehensive API documentation accessible via:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc

## Architecture

### Plugin System

The backend uses a plugin architecture for connectors:

- **Base Plugin**: `src/plugins/base.py` - Abstract base class
- **Connector Plugins**: `src/plugins/` - Individual connector implementations
- **Plugin Manager**: `src/services/plugin_manager.py` - Handles plugin registration

### Database Models

- **Users**: User accounts and authentication
- **Connectors**: Available connector definitions
- **Connections**: User connections to specific connectors
- **OAuth Tokens**: Stored OAuth credentials

### Authentication

- **JWT tokens** for API authentication
- **OAuth flows** for third-party service integration
- **State management** for secure OAuth callbacks

## API Endpoints

### Connectors
- `GET /api/connectors/` - List all available connectors
- `GET /api/connectors/{key}` - Get connector details
- `POST /api/connectors/` - Create custom connector
- `PUT /api/connectors/{key}` - Update connector
- `DELETE /api/connectors/{key}` - Delete connector

### Connections
- `GET /api/connections/` - List user connections
- `POST /api/connections/` - Create new connection
- `GET /api/connections/{id}` - Get connection details
- `PUT /api/connections/{id}` - Update connection
- `DELETE /api/connections/{id}` - Delete connection
- `POST /api/connections/{id}/test` - Test connection

### OAuth
- `GET /api/oauth/{connector}/authorize` - Initiate OAuth flow
- `GET /api/oauth/{connector}/callback` - Handle OAuth callback
- `POST /api/oauth/{connector}/callback` - Handle OAuth callback (POST)
- `DELETE /api/oauth/{connector}/revoke/{connection_id}` - Revoke OAuth token

## Configuration

### CORS Configuration

The backend is configured to accept requests from:
- Frontend URL (configurable via `FRONTEND_BASE_URL`)
- Backend URL (for development tools)

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `JWT_SECRET` | Secret key for JWT tokens | Yes | - |
| `BACKEND_BASE_URL` | Backend server URL | No | http://localhost:3001 |
| `FRONTEND_BASE_URL` | Frontend application URL | No | http://localhost:3000 |
| `{CONNECTOR}_CLIENT_ID` | OAuth client ID for connector | For OAuth | - |
| `{CONNECTOR}_CLIENT_SECRET` | OAuth client secret for connector | For OAuth | - |

## Testing

Run tests (when available):

```bash
pytest
```

## Production Deployment

For production deployment:

1. **Set secure environment variables**
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Configure SSL/TLS** for HTTPS
4. **Set up database connection pooling**
5. **Configure logging and monitoring**

Example production startup:

```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3001
```

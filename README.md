# connector-framework-manager-147069-147079

This repository contains a multi-container app:
- core_backend (FastAPI + SQLAlchemy + Alembic)
- core_frontend (Next.js)

For database schema and migration steps, see core_backend/README.md. Quick start for backend DB:

1) Configure environment:
- Copy core_backend/.env.example to core_backend/.env and set DATABASE_URL (PostgreSQL recommended)

2) Install dependencies and run migrations:
```bash
cd core_backend
pip install -r requirements.txt
alembic upgrade head
```

Notes:
- JSON fields use JSONB on PostgreSQL and JSON on SQLite.
- Unique constraints and cascades:
  - connectors.key unique
  - users.email unique
  - connections unique (user_id, connector_id) with ON DELETE CASCADE on FKs

This repository contains a multi-container app:
- core_backend (FastAPI + SQLAlchemy + Alembic)
- core_frontend (Next.js)

For database schema and migration steps, see core_backend/README.md. Quick start for backend DB:

1) Configure environment:
- Copy core_backend/.env.example to core_backend/.env and set DATABASE_URL (PostgreSQL recommended)

2) Install dependencies and run migrations:
```bash
cd core_backend
pip install -r requirements.txt
alembic upgrade head
```

Notes:
- JSON fields use JSONB on PostgreSQL and JSON on SQLite.
- Unique constraints and cascades:
  - connectors.key unique
  - users.email unique
  - connections unique (user_id, connector_id) with ON DELETE CASCADE on FKs
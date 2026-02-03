---
name: observatory
description: Launch the Claude Code Observatory - a Django-based dashboard for exploring sessions, messages, hooks, plugins, and knowledge graph data
---

# Claude Code Observatory

A comprehensive Django application for exploring and analyzing Claude Code data.

## Quick Start

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/observatory

# First time setup
uv sync
python manage.py migrate
python manage.py createsuperuser

# Run the server
python manage.py runserver 8000
```

## Access Points

- **Admin UI**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/docs/
- **API Root**: http://localhost:8000/api/

## Features

### Django Admin
Full CRUD interface for all 32 models:
- Sessions, Events, Messages
- Hooks, Plugins, Skills, Agents, Commands
- Settings profiles and values
- Subagent sessions and hierarchy
- Knowledge graph (Resources, Edges, Content)
- Vector embeddings (pgvector)

### REST API
Complete REST API with:
- ViewSets for all models
- Filtering, search, pagination
- OpenAPI/Swagger documentation
- Token authentication (optional)

## Database Setup

Requires PostgreSQL with pgvector extension:

```bash
createdb claude_observatory
psql claude_observatory -c "CREATE EXTENSION vector;"
```

## Environment Variables

Create a `.env` file or set:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production

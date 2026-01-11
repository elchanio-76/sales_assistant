# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An AI-powered sales assistant that automates prospect research, AWS solution matching, and personalized outreach generation using multi-agent workflows (LangGraph). The system uses PostgreSQL with pgvector for vector embeddings, FastAPI backend, and integrates with AWS services.

**Status:** Early development - core database models and vector services implemented, agent workflows pending.

## Development Commands

### Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies (using uv package manager)
uv pip install -r requirements.txt
```

### Database Operations

```bash
# Create database tables from models (requires empty DB first)
uv run app/models/database.py create_database

# After creating database, stamp with latest migration
alembic stamp head

# Generate new migration from model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Extract DDL from current database
uv run scripts/extract_ddl.py

# Generate ER diagram and documentation
scripts/document_db.sh  # Outputs to docs/schema.md and docs/schema.png
```

### Seed Data Management

```bash
# Load seed data (idempotent - skips existing records)
python scripts/load_seed_data.py

# Clear and reload seed data (DESTRUCTIVE)
python scripts/load_seed_data.py --clear

# Verify loaded data
python scripts/verify_seed_data.py

# Create embeddings for solutions and interactions
# Script handles both seed data and existing interactions
python scripts/create_embeddings.py
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/services/test_vector_service.py -v

# Run unit tests only
pytest tests/unit/
```

### Running the Application

```bash
# Start FastAPI server (development mode, recommended)
# Note: --reload-dir flags exclude logs/ from triggering reloads
uv run fastapi dev app/main.py --reload-dir app --reload-dir scripts

# Alternative: Start with uvicorn directly (with logs excluded)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude "logs/*"

# Health check
curl http://localhost:8000/api/v1/health

# OpenAPI documentation (when server is running)
# http://localhost:8000/docs
```

## Architecture

### Core Components

- **FastAPI Backend** (`app/main.py`): REST API with middleware for logging and error handling
- **PostgreSQL 15+ with pgvector**: Relational data + vector embeddings for semantic search
- **LangGraph Workflows** (`app/agents/`): Multi-agent orchestration (Research, Outreach, Event Matching) - *pending implementation*
- **Vector Service** (`app/services/vector_service.py`): Text chunking and embedding generation using sentence-transformers
- **Database Layer** (`app/services/db_crud.py`, `app/services/db_vector_crud.py`): CRUD operations for relational and vector data

### Data Model Structure

**Core Tables:**
- `prospects` - Sales prospects with LinkedIn profiles
- `companies` - Company information linked to industries
- `industries` - Industry classifications
- `awsolutions` - AWS solution catalog with use cases
- `interactions` - Communication history with prospects
- `outreach_drafts` - AI-generated outreach emails

**Vector Tables:**
- `solution_vectors` - Embeddings for AWS solutions (384-dim, uses all-MiniLM-L12-v2)
- `interaction_vectors` - Embeddings for prospect interactions

**Enums:**
- `ProspectStatus`: NEW, RESEARCHED, CONTACTED, ENGAGED, QUALIFIED, INACTIVE
- `InteractionType`: EMAIL, MEETING, CALL, EVENT, LINKEDIN
- `OutreachStatus`: CREATED, SENT, ACKNOWLEDGED, UNREAD, RESPONDED, DECLINED
- `PricingModels`: ON_DEMAND, SAVINGS_PLANS, RESERVED_INSTANCES, PROSERVE, SUBSCRIPTION, PPA

### Vector Search Pattern

The system uses pgvector with cosine similarity for semantic search:

```python
# Example from db_vector_crud.py
SELECT id, solution_id, embedding <=> %s AS distance
FROM solution_vectors
ORDER BY distance
LIMIT k
```

Vector operations support optional metadata filtering (industry, keywords) to refine results.

### Two-Tier Solution Matching (Planned)

1. **Tier 1 (Fast)**: Vector search in pgvector for candidate AWS solutions (<500ms)
2. **Tier 2 (Accurate)**: AWS MCP enrichment with live documentation and pricing
3. **Fallback**: If MCP unavailable, degrades gracefully to vector-only results

## Configuration

Environment variables are managed via `.env` file (use `.env.example` as template):

**Critical Settings:**
- `DB_URL`: PostgreSQL connection string (must have pgvector extension enabled)
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`: LLM provider credentials
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `TIMEZONE`: Application timezone (default: Europe/Athens)
- `MAX_CONCURRENT_LLM_CALLS`: Concurrency limit for agent workflows

**Note:** Settings class uses pydantic-settings and loads from `.env` automatically.

## Key Implementation Details

### Database Models (`app/models/database.py`)

- Uses SQLAlchemy 2.x with `Mapped[]` type hints and `mapped_column()`
- Enums defined as Python Enum classes, mapped to PostgreSQL ENUM types
- Timezone-aware datetime fields use `pytz.timezone("Europe/Athens")`
- Vector columns use `pgvector.sqlalchemy.Vector` type with dimension 384

### CRUD Operations

- **Relational CRUD**: `app/services/db_crud.py` - Standard SQLAlchemy operations
- **Vector CRUD**: `app/services/db_vector_crud.py` - Specialized for vector search with metadata filtering

When adding new CRUD operations:
1. Add function to appropriate service file
2. Use SQLAlchemy sessions properly (commit on write, rollback on error)
3. For vector operations, ensure embeddings are generated via `vector_service.get_embedding()`

### Converting SQLAlchemy Models to Pydantic (FastAPI Response Models)

**Problem**: SQLAlchemy ORM objects cannot be unpacked with `**` like dictionaries.

**Solution**: Use Pydantic's `from_attributes=True` config and `model_validate()` method:

```python
# 1. Configure Pydantic model (in app/models/api.py)
class ProspectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode

    id: int
    full_name: str
    # ... other fields

# 2. Convert in endpoint (in app/api/prospects.py)
@router.get("/", response_model=list[ProspectResponse])
async def get_prospects():
    prospects = get_all_prospects()  # Returns list of SQLAlchemy objects
    return [ProspectResponse.model_validate(prospect) for prospect in prospects]
```

**Key points**:
- Add `model_config = ConfigDict(from_attributes=True)` to ALL Response models
- Use `model_validate()` instead of `**object` unpacking
- FastAPI automatically serializes to JSON when `response_model` is specified
- All Response models in `api.py` already have this config enabled

### Logging

- Structured JSON logging using custom `LogEntry` model (`app/utils/logging.py`)
- Logs written to `logs/{date}app.log` with daily rotation
- Request/response logging via FastAPI middleware
- Log levels configurable via `LOG_LEVEL` environment variable

### Testing Strategy

- **Unit tests** in `tests/unit/`: Focus on services (vector operations, CRUD, business logic)
- **Database tests** use `TEST_DATABASE_URL` (separate test database)
- **Fixtures** in `tests/conftest.py`: Database engine, sessions, sample data
- Tests preserve migration history (truncate data, don't drop tables)
- Target: 70%+ coverage for core services

## Important Patterns

### Seed Data Loading

The seed data system is idempotent and maintains referential integrity:

1. **Order matters**: Industries → Companies → Prospects → Solutions
2. **JSON fields**: Solutions table stores `use_cases` and `keywords` as JSONB
3. **Duplicate handling**: CSV loader skips existing records by unique constraints
4. **Embeddings**: Separate script creates vector embeddings after data load

### Error Handling

- LLM API failures: Exponential backoff retry (3 attempts) - *to be implemented*
- Database errors: Transaction rollback, detailed logging
- MCP failures: Graceful degradation to vector-only results - *to be implemented*

### Vector Embedding Workflow

1. Text → Chunking (250 words, 50 overlap) via `chunk_text()`
2. Chunks → Embeddings via `get_embedding()` using sentence-transformers
3. Embeddings → PostgreSQL via `db_vector_crud.create_vectors()`
4. Search → Cosine similarity via pgvector `<=>` operator

## Migration Guide

When changing database schema:

1. **Modify models** in `app/models/database.py`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration** in `alembic/versions/` (autogenerate isn't perfect)
4. **Test migration**: Apply on test database, verify schema
5. **Apply to dev**: `alembic upgrade head`

**Enum handling**: Requires `enum34` package. For enum changes, may need manual migration edits using `alembic-postgresql-enum`.

## API Structure

**Current endpoints** (more to be added):
- `GET /api/v1/health` - Health check

**Planned endpoints** (see SPECS.md section 4):
- Prospects: CRUD, CSV import
- Research: Trigger workflows, retrieve results
- Outreach: Generate drafts, manage interactions
- Events: Match prospects, generate invitations
- Solutions: Search, retrieve details

All endpoints use `/api/v1` prefix. FastAPI auto-generates OpenAPI docs at `/docs`.

## Dependencies

**Core:**
- fastapi[standard] - Web framework
- sqlalchemy >= 2.0 - ORM
- alembic[tz] - Migrations
- pgvector - Vector extension support
- psycopg2-binary - PostgreSQL driver
- sentence-transformers - Embeddings

**LLM Stack** (planned):
- langgraph - Workflow orchestration
- langchain - LLM abstractions
- openai, anthropic - LLM providers

**Testing:**
- pytest, pytest-cov - Testing framework
- coverage - Code coverage

**Utilities:**
- pydantic, pydantic-settings - Config and validation
- python-dotenv - Environment management
- pytz - Timezone handling

## Development Workflow

1. **Create feature branch** (optional for capstone)
2. **Implement changes** with unit tests
3. **Run tests**: `pytest --cov=app`
4. **Generate migration** if schema changed
5. **Update seed data** if needed
6. **Manual testing** via curl or future Gradio UI
7. **Merge to main** and tag stable versions

## Future Development

**Agent Workflows** (high priority):
- Research workflow: Company analysis, tech stack inference, solution matching
- Outreach workflow: Personalized email generation using research context
- Event matching workflow: Prospect scoring and invitation generation

**UI Layer** (medium priority):
- Gradio interface in separate container
- Workflow execution and result viewing
- CSV upload for bulk prospect import

**AWS Integration** (medium priority):
- MCP servers for live AWS documentation and pricing
- Reference architecture search agent

**Deployment** (planned):
- Docker Compose for local development
- AWS ECS deployment with RDS PostgreSQL

## Troubleshooting

**Migration issues:**
- Check enum types exist: `\dT+ prospect_status` in psql
- Manual enum migration may be needed for type changes

**Vector search errors:**
- Verify pgvector extension: `SELECT * FROM pg_extension WHERE extname = 'pgvector'`
- Check embedding dimensions match (384 for all-MiniLM-L12-v2)

**Seed data loading:**
- Ensure database schema is current: `alembic upgrade head`
- Check CSV format (JSON arrays must be valid JSON)
- Verify referential integrity order (industries before companies)

**Test database:**
- Use separate `sales_test` database
- Set `TEST_DATABASE_URL` environment variable
- Tests truncate data but preserve schema

## Additional Resources

- **SPECS.md**: Comprehensive technical specifications (40-60 hour capstone project)
- **README.md**: Installation and basic usage
- **scripts/README.md**: Detailed seed data and script documentation
- **docs/schema.md**: Auto-generated database documentation

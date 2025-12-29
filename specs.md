# Agentic Sales Assistant - Technical Specifications v1.0.0

## 1. Project Overview

### 1.1 Purpose
An AI-powered sales assistant that automates prospect research, AWS solution matching, and personalized outreach generation for enterprise account managers. The system leverages multi-agent workflows to enrich prospect data, identify relevant AWS solutions, and generate contextual sales communications.

### 1.2 Scope
**Capstone Project Timeline:** 40-60 hours  
**Target Version:** v1.0.0 (Capstone Submission)  
**Deployment Model:** Hybrid (Local development, AWS ECS production-ready)

### 1.3 Key Capabilities
- Prospect data import and enrichment
- Automated company research and analysis
- Two-tier AWS solution matching (vector search + MCP)
- Personalized outreach generation
- Event-based prospect matching and invitation generation
- Reference architecture search assistant

---

## 2. Architecture

### 2.1 System Components
```
┌─────────────────────────────────────────────────────────────┐
│                        Gradio UI                             │
│                   (Separate Container)                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Research   │  │   Outreach   │  │Event Matching│     │
│  │   Workflow   │  │   Workflow   │  │   Workflow   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Vector Service│  │Solution      │  │AWS MCP       │     │
│  │              │  │Matcher       │  │Service       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────┬─────────────────┬──────────────────┬──────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Qdrant    │  │External MCP  │
│              │  │ Vector Store │  │  Servers     │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 2.2 Technology Stack

**Backend Framework:**
- FastAPI (Python 3.11+)
- Pydantic v2 (data validation)
- SQLAlchemy 2.x (ORM and migrations)

**Agent Orchestration:**
- LangGraph (workflow orchestration)
- LangChain providers (multi-model support)
- LangSmith (agent debugging and tracing)

**LLM Providers:**
- Primary: OpenAI (GPT-4), Anthropic (Claude Sonnet 4.5)
- Configurable via LangGraph provider abstraction

**Data Storage:**
- PostgreSQL 15+ (relational data)
- Qdrant (vector embeddings)

**Vector Embeddings:**
- sentence-transformers (`all-MiniLM-L6-v2`)

**Frontend:**
- Gradio (separate containerized service)

**Infrastructure:**
- Docker & Docker Compose (local dev)
- AWS ECS (production deployment)
- AWS RDS PostgreSQL (production database)
- Qdrant Cloud (production vector store)

**Additional Services:**
- AWS MCP servers (live AWS documentation and pricing)

### 2.3 Deployment Architecture

**Local Development:**
```
Docker Compose:
├── gradio-ui (container)
├── fastapi-backend (container)
├── existing PostgreSQL (host service)
└── existing Qdrant (host service)
```

**AWS ECS Production:**
```
ECS Cluster:
├── Gradio UI Service (Fargate task)
├── FastAPI Backend Service (Fargate task)
├── RDS PostgreSQL (managed)
├── Qdrant Cloud (managed)
└── AWS Secrets Manager (API keys, DB credentials)
```

---

## 3. Data Model

### 3.1 PostgreSQL Schema

**Core Entities:**
```python
class Prospect:
    id: int (PK)
    linkedin_url: str (unique)
    full_name: str
    title: str
    company_name: str
    company_size: Optional[str]
    industry: Optional[str]
    location: Optional[str]
    status: ProspectStatus (enum)
    last_contacted: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class Company:
    id: int (PK)
    name: str (unique)
    industry: str
    size: Optional[str]
    linkedin_url: Optional[str]
    website: Optional[str]
    tech_stack: JSONB (nullable)
    pain_points: JSONB (nullable)
    created_at: datetime
    updated_at: datetime

class AWSolution:
    id: int (PK)
    name: str (unique)
    category: str
    description: text
    use_cases: JSONB
    industries: JSONB
    keywords: JSONB
    pricing_model: str
    last_updated: datetime

class ProspectResearch:
    id: int (PK)
    prospect_id: int (FK → Prospect)
    research_summary: text
    key_insights: JSONB
    recommended_solutions: JSONB
    confidence_score: float
    sources: JSONB
    created_at: datetime

class Interaction:
    id: int (PK)
    prospect_id: int (FK → Prospect)
    interaction_type: InteractionType (enum)
    subject: Optional[str]
    content: text
    sentiment: Optional[str]
    outcome: Optional[str]
    interaction_date: datetime
    created_at: datetime

class OutreachDraft:
    id: int (PK)
    prospect_id: int (FK → Prospect)
    event_id: Optional[int] (FK → Event)
    subject: str
    body: text
    suggested_solutions: JSONB
    context_used: JSONB
    created_at: datetime
    sent_at: Optional[datetime]

class Event:
    id: int (PK)
    title: str
    description: text
    event_type: str
    event_date: datetime
    target_industries: JSONB
    target_roles: JSONB
    aws_solutions_featured: JSONB
    created_at: datetime

class LLMUsageLog:
    id: int (PK)
    workflow_name: str
    node_name: str
    provider: str (openai/anthropic)
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: decimal
    latency_ms: int
    created_at: datetime
```

**Enums:**
```python
class ProspectStatus(str, Enum):
    NEW = "new"
    RESEARCHED = "researched"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    INACTIVE = "inactive"

class InteractionType(str, Enum):
    EMAIL = "email"
    MEETING = "meeting"
    CALL = "call"
    EVENT = "event"
    LINKEDIN = "linkedin"
```

### 3.2 Qdrant Vector Store Schema

**Collections:**

**1. aws_solutions**
- Vector dimension: 384 (all-MiniLM-L6-v2)
- Distance metric: Cosine
- Payload schema:
```python
{
    "solution_id": int,
    "name": str,
    "category": str,
    "description": str,
    "use_cases": list[str],
    "industries": list[str],
    "keywords": list[str],
    "pricing_model": str,
    "last_updated": str (ISO datetime)
}
```

**2. reference_architectures**
- Vector dimension: 384
- Distance metric: Cosine
- Payload schema:
```python
{
    "title": str,
    "solutions_used": list[str],
    "industry": str,
    "description": str,
    "compliance_frameworks": list[str],
    "diagram_url": str,
    "doc_url": str
}
```

**3. past_communications**
- Vector dimension: 384
- Distance metric: Cosine
- Payload schema:
```python
{
    "prospect_id": int,
    "company": str,
    "subject": str,
    "content": str,
    "solutions_mentioned": list[str],
    "outcome": str,
    "date": str (ISO datetime)
}
```

---

## 4. API Design

### 4.1 RESTful Endpoints

**Base URL:** `/api/v1`

**Prospects:**
```
POST   /prospects
GET    /prospects
GET    /prospects/{prospect_id}
PATCH  /prospects/{prospect_id}
POST   /prospects/import/csv
GET    /prospects/import/template
```

**Research:**
```
POST   /prospects/{prospect_id}/research
GET    /prospects/{prospect_id}/research
GET    /prospects/{prospect_id}/research/latest
```

**Outreach:**
```
POST   /prospects/{prospect_id}/outreach
GET    /prospects/{prospect_id}/outreach
PATCH  /outreach/{draft_id}
```

**Events:**
```
POST   /events
GET    /events
GET    /events/{event_id}
POST   /events/{event_id}/match-prospects
```

**AWS Solutions:**
```
GET    /solutions
POST   /solutions
GET    /solutions/search
```

**Interactions:**
```
POST   /prospects/{prospect_id}/interactions
GET    /prospects/{prospect_id}/interactions
```

**System:**
```
GET    /health
GET    /metrics/llm-usage
```

### 4.2 Request/Response Models

See Section 3.1 for Pydantic schemas corresponding to each endpoint.

### 4.3 OpenAPI Documentation

FastAPI auto-generates OpenAPI 3.0 schema at `/docs` (Swagger UI) and `/redoc`.

**Curl Test Scripts:**
- Generated from OpenAPI schema using LLM
- Stored in `/tests/api/curl_tests/`
- Regenerated on schema changes

---

## 5. LangGraph Workflows

### 5.1 Research Workflow

**Purpose:** Enrich prospect data, analyze company, match AWS solutions

**State Schema:**
```python
class ResearchState(TypedDict):
    prospect_id: int
    prospect: dict
    company: dict
    manual_context: str
    company_research: str
    tech_stack_analysis: dict
    pain_points: list[str]
    market_position: str
    recommended_solutions: list[dict]
    reference_architectures: list[dict]
    research_summary: str
    confidence_score: float
    sources: list[str]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next_step: str
```

**Node Sequence:**
1. `gather_context` - Load prospect/company data from DB
2. `research_company` - Web search for company intel
3. `analyze_tech_stack` - Infer technology stack and opportunities
4. `identify_pain_points` - Extract business challenges
5. `match_solutions` - Two-tier AWS solution matching (vector + MCP)
6. `synthesize_research` - Generate executive summary

**Error Handling:**
- LLM API failures: exponential backoff retry (3 attempts)
- MCP failures: graceful degradation to vector-only results
- All errors logged with full context

**Persistence:**
- Final state saved to `ProspectResearch` table
- Intermediate states logged to JSON file for debugging

### 5.2 Outreach Generation Workflow

**Purpose:** Generate personalized sales emails based on research

**State Schema:**
```python
class OutreachState(TypedDict):
    prospect_id: int
    event_id: Optional[int]
    custom_context: Optional[str]
    prospect: dict
    company: dict
    research: dict
    event: Optional[dict]
    similar_communications: list[dict]
    email_strategy: dict
    draft_subject: str
    draft_body: str
    suggested_solutions: list[str]
    messages: Annotated[Sequence[BaseMessage], operator.add]
```

**Node Sequence:**
1. `load_context` - Load prospect, research, event data
2. `analyze_similar_wins` - Vector search for successful past emails
3. `plan_email_strategy` - Determine approach, tone, solutions to highlight
4. `generate_subject` - Create compelling subject line
5. `generate_body` - Write email body (150-200 words)
6. `refine_draft` - Grammar check and tone refinement

**Error Handling:**
- Same retry logic as Research workflow
- If similar_communications empty, proceed without historical patterns

**Persistence:**
- Draft saved to `OutreachDraft` table
- Can be edited via PATCH endpoint before marking as sent

### 5.3 Event Matching Workflow

**Purpose:** Identify relevant prospects for events, generate invitations

**State Schema:**
```python
class EventMatchingState(TypedDict):
    event_id: int
    event: dict
    candidate_prospects: list[dict]
    scored_prospects: list[dict]
    top_matches: list[dict]
    invitation_drafts: list[dict]
    messages: Annotated[Sequence[BaseMessage], operator.add]
```

**Node Sequence:**
1. `load_event` - Fetch event details
2. `find_candidates` - SQL + vector search for matching prospects
3. `score_relevance` - LLM scores each candidate (0-100)
4. `select_top_matches` - Filter top 20 or score >= 70
5. `generate_invitations` - Call Outreach workflow for each match

**Error Handling:**
- Same retry logic as other workflows
- If scoring fails for a prospect, skip and continue

**Concurrency Control:**
- Max 5 concurrent LLM calls during scoring phase
- Configurable via `MAX_CONCURRENT_LLM_CALLS` env var

**Persistence:**
- Invitation drafts saved to `OutreachDraft` table with `event_id` reference

### 5.4 Reference Architecture Search Agent

**Purpose:** Search AWS reference architectures on-demand (not pre-indexed)

**Implementation:**
- Standalone agent (not a full workflow)
- Triggered by user query or automatically during research
- Uses web search + AWS documentation sites
- Returns relevant architecture links and summaries
- Serves dual purpose: capstone efficiency + production utility

---

## 6. Two-Tier AWS Solution Matching

### 6.1 Tier 1: Vector Store (Fast Candidate Generation)

**Purpose:** Sub-second retrieval of relevant AWS solutions

**Process:**
1. Embed prospect context (industry, pain points, tech stack)
2. Search `aws_solutions` collection (top 10 candidates)
3. Search `reference_architectures` collection (top 3)
4. Search `past_communications` for similar successful interactions

**Filters:**
- Industry matching (exact or "all")
- Optional: company size, specific keywords

**Response Time:** < 500ms

### 6.2 Tier 2: AWS MCP Layer (Live Accuracy)

**Purpose:** Enrich top candidates with current information

**Process:**
1. Take top 5 solutions from Tier 1
2. Query AWS MCP servers for:
   - Latest documentation and features
   - Current pricing estimates (based on company size)
   - Compliance/region compatibility checks
3. Return enriched solution data

**MCP Servers Used:**
- AWS Documentation MCP (hypothetical: `https://mcp.aws.amazon.com/sse`)
- Pricing Calculator MCP
- (Note: If official AWS MCP servers unavailable, fallback to vector-only or build custom wrapper)

**Fallback Strategy:**
- If MCP call fails/times out: use Tier 1 data only
- If MCP unavailable: entire system degrades to vector-only (still functional)

**Caching:**
- MCP responses cached in-memory for 24 hours (per solution)
- Cache key: `solution_name:usage_pattern_hash`

### 6.3 Integration

Located in `services/solution_matcher.py`:
```python
class SolutionMatcher:
    async def match_solutions_for_prospect(
        prospect: Prospect,
        company: Company,
        research: ProspectResearch
    ) -> dict:
        # Tier 1: Vector search
        candidates = vector_service.search_solutions(...)
        
        # Tier 2: MCP enrichment
        enriched = await mcp_service.enrich_solutions(candidates[:5])
        
        return {
            "recommended_solutions": enriched,
            "reference_architectures": ref_archs,
            "similar_past_wins": past_comms
        }
```

---

## 7. Data Management

### 7.1 Database Migrations

**Tool:** SQLAlchemy Alembic

**Migration Commands:**
```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Location:** `/alembic/versions/`

### 7.2 Seed Data Strategy

**AWS Solutions:**
- Generate CSV with LLM (solution descriptions, use cases, keywords)
- Ingest via Python script: `scripts/seed_aws_solutions.py`
- Automatically embed and store in Qdrant

**Test Prospects:**
- Generate realistic CSV with LLM (names, companies, industries)
- Import via `/api/prospects/import/csv` endpoint
- Reflects production workflow

**Reference Architectures:**
- NOT pre-ingested (too much effort)
- Use Reference Architecture Search Agent on-demand
- Agent searches AWS architecture center in real-time

**Seed Data Files:**
- Located in `/data/seeds/`
- Versioned with git (not ignored)
- Scripts in `/scripts/seed_*.py`

### 7.3 Vector Store Management

**Initialization:**
```python
# scripts/init_qdrant.py
- Create collections
- Set up indexes
- Configure distance metrics
```

**Population:**
```python
# scripts/populate_vectors.py
- Read AWS solutions from PostgreSQL
- Generate embeddings
- Upsert to Qdrant collections
```

**Maintenance:**
- Periodic re-embedding if solution descriptions change
- Manual trigger via admin endpoint (future enhancement)

---

## 8. Configuration Management

### 8.1 Environment Variables

**Local Development (`.env`):**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sales_assistant

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # optional for local

# LLM Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# LangSmith (optional but recommended)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=sales-assistant-dev

# Application
LOG_LEVEL=INFO
MAX_CONCURRENT_LLM_CALLS=5
LLM_RETRY_ATTEMPTS=3
LLM_RETRY_BACKOFF_FACTOR=2

# AWS (for ECS deployment)
AWS_REGION=eu-central-1
AWS_SECRETS_MANAGER_NAME=sales-assistant/prod
```

**AWS ECS (Secrets Manager):**
- All secrets stored in AWS Secrets Manager
- Retrieved on container startup
- Secret name format: `sales-assistant/{environment}/{key}`

### 8.2 Configuration Files

**`config/settings.py`:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    qdrant_url: str
    qdrant_api_key: Optional[str] = None
    
    openai_api_key: str
    anthropic_api_key: str
    
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "sales-assistant"
    
    log_level: str = "INFO"
    max_concurrent_llm_calls: int = 5
    llm_retry_attempts: int = 3
    llm_retry_backoff_factor: int = 2
    
    aws_region: str = "eu-central-1"
    
    class Config:
        env_file = ".env"
```

---

## 9. Logging and Observability

### 9.1 Application Logging

**Format:** Structured JSON logs

**Schema:**
```json
{
    "timestamp": "2025-01-15T10:30:45.123Z",
    "level": "INFO",
    "service": "fastapi-backend",
    "module": "agents.research_workflow",
    "function": "research_company_node",
    "message": "Starting company research",
    "context": {
        "prospect_id": 42,
        "company": "Acme Corp"
    },
    "trace_id": "uuid"
}
```

**Destinations:**
- Local: `/logs/app.log` (rotated daily)
- ECS: CloudWatch Logs (future enhancement)

**Log Levels:**
- ERROR: Unrecoverable failures
- WARNING: Recoverable issues (retry triggered, degraded mode)
- INFO: Workflow milestones, API requests
- DEBUG: Detailed execution (disabled in production)

### 9.2 LLM Observability

**Tool:** LangSmith

**Tracked Metrics:**
- Prompt templates used
- Input/output tokens per call
- Latency per LLM request
- Agent decision paths
- Error rates by workflow/node

**Access:**
- Dashboard: https://smith.langchain.com
- Project: `sales-assistant-{environment}`

**Cost Tracking:**
```python
# Logged to LLMUsageLog table after each call
{
    "workflow": "research",
    "node": "research_company",
    "provider": "openai",
    "model": "gpt-4-turbo",
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801,
    "estimated_cost": 0.0234,  # USD
    "latency_ms": 2345
}
```

**Cost Aggregation Endpoint:**
```
GET /api/metrics/llm-usage?start_date=2025-01-01&end_date=2025-01-31
```

### 9.3 Performance Metrics

**Tracked via Middleware:**
- API endpoint latency (p50, p95, p99)
- Request/response sizes
- Error rates by endpoint
- Workflow execution times

**Future Enhancement:** Prometheus + Grafana integration

---

## 10. Testing Strategy

### 10.1 Testing Framework

**Tool:** pytest

**Test Structure:**
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_vector_service.py
│   │   ├── test_solution_matcher.py
│   │   └── test_database.py
│   └── utils/
│       └── test_helpers.py
├── integration/
│   ├── test_research_workflow.py
│   ├── test_outreach_workflow.py
│   └── test_event_matching_workflow.py
├── api/
│   ├── test_prospects_endpoints.py
│   ├── test_research_endpoints.py
│   └── test_outreach_endpoints.py
└── fixtures/
    ├── mock_prospects.json
    └── mock_research.json
```

### 10.2 Test Coverage

**Unit Tests (Required):**
- Vector service (search, embedding, similarity)
- Solution matcher (tier 1 + tier 2)
- Database operations (CRUD, queries)
- Pydantic models (validation)
- Helper utilities

**API Tests (Required):**
- All endpoints (happy path)
- Error cases (400, 404, 500)
- Authentication (future)
- Request validation

**Integration Tests (Optional/Selective):**
- Research workflow (end-to-end with mocked LLM)
- Outreach workflow (with mocked vector store)
- Event matching (with mocked DB + LLM)
- Decision: Implement if time permits and practical

**Target Coverage:** 70%+ for unit tests, 50%+ for API tests

### 10.3 Test Execution

**Commands:**
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# API tests only
pytest tests/api/

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/services/test_vector_service.py -v
```

**CI/CD Integration:** Manual for capstone; GitHub Actions in future

### 10.4 Curl Test Scripts

**Generation Strategy:**
- Use LLM to generate curl scripts from OpenAPI schema
- Stored in `tests/api/curl_tests/`
- Organized by endpoint group (prospects, research, outreach, etc.)

**Regeneration Trigger:**
- Manual: `scripts/generate_curl_tests.py`
- Prompt LLM with OpenAPI JSON + example request/response

**Example Structure:**
```bash
# tests/api/curl_tests/prospects.sh

# Create prospect
curl -X POST http://localhost:8000/api/v1/prospects \
  -H "Content-Type: application/json" \
  -d '{
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "full_name": "John Doe",
    "title": "CTO",
    "company_name": "Acme Corp",
    "industry": "Financial Services"
  }'

# Get prospect
curl http://localhost:8000/api/v1/prospects/1
```

---

## 11. Deployment

### 11.1 Local Development Setup

**Prerequisites:**
- Docker & Docker Compose
- Python 3.11+
- Existing PostgreSQL service (port 5432)
- Existing Qdrant service (port 6333)

**Steps:**
```bash
# 1. Clone repository
git clone <repo-url>
cd sales-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
alembic upgrade head
python scripts/seed_aws_solutions.py

# 6. Initialize Qdrant
python scripts/init_qdrant.py
python scripts/populate_vectors.py

# 7. Start services
docker-compose up -d

# 8. Verify
curl http://localhost:8000/health
curl http://localhost:7860  # Gradio UI
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@host.docker.internal:5432/sales_assistant
      - QDRANT_URL=http://host.docker.internal:6333
    env_file:
      - .env
    depends_on:
      - gradio-ui
    volumes:
      - ./logs:/app/logs

  gradio-ui:
    build: ./ui
    ports:
      - "7860:7860"
    environment:
      - BACKEND_URL=http://backend:8000
```

### 11.2 AWS ECS Deployment

**Architecture:**
```
ALB → ECS Service (Backend) → RDS PostgreSQL
                            → Qdrant Cloud
     → ECS Service (Gradio UI)
```

**ECS Task Definitions:**

**Backend Task:**
```json
{
  "family": "sales-assistant-backend",
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [{
    "name": "backend",
    "image": "<ecr-repo>/sales-assistant-backend:v1.0.0",
    "portMappings": [{"containerPort": 8000}],
    "environment": [
      {"name": "AWS_REGION", "value": "eu-central-1"}
    ],
    "secrets": [
      {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..."},
      {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/sales-assistant-backend",
        "awslogs-region": "eu-central-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
```

**Gradio UI Task:** (Similar structure, port 7860)

**Deployment Steps:**
```bash
# 1. Build and push Docker images
docker build -t sales-assistant-backend:v1.0.0 ./backend
docker tag sales-assistant-backend:v1.0.0 <ecr-repo>/sales-assistant-backend:v1.0.0
docker push <ecr-repo>/sales-assistant-backend:v1.0.0

# 2. Update task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 3. Update service
aws ecs update-service \
  --cluster sales-assistant-cluster \
  --service backend \
  --task-definition sales-assistant-backend:v1.0.0 \
  --force-new-deployment

# 4. Run database migrations (one-time task)
aws ecs run-task \
  --cluster sales-assistant-cluster \
  --task-definition migration-task \
  --launch-type FARGATE
```

**Infrastructure (Terraform or Manual):**
- VPC with public/private subnets
- RDS PostgreSQL (db.t3.medium)
- Application Load Balancer
- ECS Cluster (Fargate)
- Secrets Manager for credentials
- CloudWatch Log Groups

---

## 12. Security Considerations

### 12.1 API Security

**Authentication/Authorization:**
- MVP: None (single-user assumption)
- Future: OAuth2 with JWT tokens

**Input Validation:**
- Pydantic models enforce schema
- SQLAlchemy prevents SQL injection
- File uploads: whitelist CSV/TXT/DOCX extensions, size limits (10MB)

**Rate Limiting:**
- Future: API Gateway throttling (1000 req/min)

### 12.2 Secrets Management

**Local:**
- `.env` file (git-ignored)
- Never commit API keys

**Production:**
- AWS Secrets Manager
- IAM roles for ECS tasks (no hardcoded credentials)
- Secrets rotation policy (90 days)

### 12.3 Data Privacy

**PII Handling:**
- Prospect data contains names, titles, LinkedIn URLs
- No email addresses or phone numbers stored (unless user imports)
- GDPR compliance: not addressed in MVP (future concern)

**LLM Data:**
- Prompts may contain PII sent to OpenAI/Anthropic
- Review provider terms of service
- Consider data retention policies

---

## 13. Error Handling and Resilience

### 13.1 LLM API Failures

**Strategy:** Exponential backoff retry

**Implementation:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    reraise=True
)
async def call_llm(prompt: str) -> str:
    # LLM API call
    pass
```

**Logging:**
- Log each attempt with context
- Log final failure with full traceback

### 13.2 Two-Tier Degradation

**MCP Failures:**
- If Tier 2 (MCP) fails, return Tier 1 (vector) results only
- Add warning flag in response: `"mcp_unavailable": true`
- Log degraded operation

**Vector Store Failures:**
- If Qdrant unreachable, workflows fail gracefully
- Return error to API caller with clear message
- Alternative: fallback to PostgreSQL full-text search (future)

### 13.3 Database Failures

**Connection Pooling:**
- SQLAlchemy pool size: 5-20
- Timeouts: 30 seconds

**Retry Logic:**
- Transient errors: retry with backoff
- Persistent errors: fail immediately

---

## 14. Performance Optimization

### 14.1 Concurrency Control

**LLM Calls:**
- Max concurrent calls: 5 (configurable)
- Semaphore in event matching workflow
- Prevents rate limit exhaustion

**Background Tasks:**
- FastAPI BackgroundTasks for long-running workflows
- Return job ID immediately, poll for status

### 14.2 Caching

**MCP Responses:**
- In-memory cache (TTL: 24 hours)
- Cache key: `solution_name:usage_pattern_hash`
- Shared across requests

**Vector Embeddings:**
- AWS solutions pre-embedded in Qdrant (acts as cache)
- Regenerate only on data updates

**Future:** Redis for distributed caching (ECS multi-instance)

### 14.3 Database Optimization

**Indexes:**
- `Prospect.linkedin_url` (unique)
- `Prospect.status`
- `ProspectResearch.prospect_id`
- `OutreachDraft.prospect_id`
- `LLMUsageLog.created_at` (for time-range queries)

**Query Optimization:**
- Use SQLAlchemy lazy loading strategically
- Paginate large result sets (default: 50 per page)

---

## 15. Gradio UI Specifications

### 15.1 Container Architecture

**Deployment:** Separate Docker container from FastAPI backend

**Communication:** HTTP requests to FastAPI backend API

**Port:** 7860 (default Gradio port)

### 15.2 Core Functionality

**Tabs/Pages:**

1. **Workflow Execution**
   - Dropdown: Select workflow (Research / Outreach / Event Matching)
   - Inputs (dynamic based on selection):
     - Research: Prospect ID
     - Outreach: Prospect ID, Event ID (optional), Custom Context
     - Event Matching: Event ID
   - Button: "Run Workflow"
   - Output: JSON result or formatted summary

2. **View Results**
   - Prospect selector (dropdown or search)
   - Tabs:
     - Research Summary
     - Outreach Drafts (list, clickable to view full draft)
     - Interactions History
   - Actions: Download as PDF, Copy to clipboard

3. **Upload Context**
   - File uploader (CSV, TXT, DOCX, PDF)
   - Upload type selector:
     - Bulk Prospect Import (CSV)
     - Customer Communication (email/doc)
     - Event Details
   - Upload button
   - Status: Success/Error with details

4. **Dashboard (Optional/Future)**
   - Prospect count by status (bar chart)
   - LLM usage summary (last 7 days)
   - Recent activity log

### 15.3 UI Framework

**Implementation:**
```python
import gradio as gr
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def run_workflow(workflow_type, prospect_id, event_id, custom_context):
    if workflow_type == "Research":
        response = requests.post(
            f"{BACKEND_URL}/api/v1/prospects/{prospect_id}/research"
        )
    # ... other workflows
    return response.json()

def upload_csv(file):
    files = {"file": file}
    response = requests.post(
        f"{BACKEND_URL}/api/v1/prospects/import/csv",
        files=files
    )
    return response.json()

with gr.Blocks() as app:
    with gr.Tab("Workflow Execution"):
        workflow = gr.Dropdown(["Research", "Outreach", "Event Matching"])
        prospect_id = gr.Number(label="Prospect ID")
        run_btn = gr.Button("Run")
        output = gr.JSON()
        run_btn.click(run_workflow, [workflow, prospect_id], output)
    
    with gr.Tab("Upload Context"):
        file = gr.File(label="Upload CSV/Doc")
        upload_type = gr.Radio(["Prospects", "Communication", "Event"])
        upload_btn = gr.Button("Upload")
        upload_output = gr.JSON()
        upload_btn.click(upload_csv, file, upload_output)

app.launch(server_name="0.0.0.0", server_port=7860)
```

### 15.4 Design Principles

- Simple, functional (not polished design)
- Clear labels and instructions
- Error messages displayed prominently
- No authentication (single-user MVP)

---

## 16. Project Structure
```
sales-assistant/
├── README.md
├── SPECS.md (this document)
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
├── alembic.ini
├── pytest.ini
│
├── alembic/
│   ├── env.py
│   └── versions/
│       └── (migration files)
│
├── app/
│   ├── __init__.py
│   ├── main.py  (FastAPI app)
│   ├── config/
│   │   └── settings.py
│   ├── models/
│   │   ├── database.py  (SQLAlchemy models)
│   │   └── api.py  (Pydantic request/response models)
│   ├── agents/
│   │   ├── research_workflow.py
│   │   ├── outreach_workflow.py
│   │   └── event_matching_workflow.py
│   ├── services/
│   │   ├── vector_service.py
│   │   ├── solution_matcher.py
│   │   ├── aws_mcp_service.py
│   │   └── database.py  (CRUD operations)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── dependencies.py
│   └── utils/
│       ├── logging.py
│       └── helpers.py
│
├── ui/
│   ├── Dockerfile
│   ├── app.py  (Gradio app)
│   └── requirements.txt
│
├── backend/
│   ├── Dockerfile
│   └── (references /app)
│
├── scripts/
│   ├── seed_aws_solutions.py
│   ├── init_qdrant.py
│   ├── populate_vectors.py
│   └── generate_curl_tests.py
│
├── data/
│   └── seeds/
│       ├── aws_solutions.csv
│       └── test_prospects.csv
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py  (fixtures)
│   ├── unit/
│   │   └── services/
│   ├── integration/
│   └── api/
│       └── curl_tests/
│
└── logs/
    └── (git-ignored)
```

---

## 17. Development Workflow

### 17.1 Version Control

**Repository:** Git (GitHub/GitLab)

**Branching Strategy:**
- `main` branch for stable code
- Feature branches as needed: `feature/research-workflow`
- Capstone submission tagged as `v1.0.0`

**Commit Messages:**
- Use conventional commits (optional): `feat:`, `fix:`, `docs:`

### 17.2 Development Cycle

1. **Feature development:**
   - Create branch (optional)
   - Implement feature
   - Write unit tests
   - Manual testing via curl/Gradio UI

2. **Code review:**
   - Self-review (capstone context)
   - Use LLM for code review suggestions (optional)

3. **Testing:**
   - Run pytest suite
   - Verify API endpoints
   - Test workflows end-to-end

4. **Documentation:**
   - Update docstrings
   - Use doc AI agent to sync with code changes
   - Update SPECS.md if design changes

5. **Merge to main:**
   - Tag stable versions (v0.1.0, v0.2.0, etc.)
   - v1.0.0 = capstone submission

### 17.3 Documentation Strategy

**Synchronization:**
- Code changes → Doc AI agent generates updates
- SPECS.md, README.md stay in sync with implementation
- OpenAPI schema auto-generated by FastAPI

**Doc AI Agent:**
- Prompt: "Update documentation to reflect code changes in <file>"
- Agent reads code, compares to docs, suggests edits
- Human review before committing

---

## 18. Future Enhancements (Post-Capstone)

**Phase 2 (v1.1.0):**
- Analytics dashboard (prospect pipeline, conversion rates)
- Natural language query interface
- Email sending integration (AWS SES)
- A/B testing for outreach strategies

**Phase 3 (v1.2.0):**
- Authentication/authorization (multi-user)
- CRM integration (Salesforce API)
- Lambda refactoring for cost optimization
- Workflow resumption after failures

**Phase 4 (v2.0.0):**
- Real-time collaboration (WebSocket updates)
- Advanced analytics (predictive lead scoring)
- Mobile app (React Native)
- Multi-language support

---

## 19. Success Criteria (Capstone)

**Functional Requirements:**
- ✅ Import prospects via CSV
- ✅ Research workflow generates actionable summaries
- ✅ Outreach workflow produces personalized emails
- ✅ Event matching identifies relevant prospects
- ✅ Two-tier solution matching works (vector + MCP)
- ✅ Gradio UI enables workflow execution and result viewing
- ✅ Reference architecture search agent functional

**Technical Requirements:**
- ✅ Deployable on AWS ECS (infrastructure documented)
- ✅ Unit tests (70%+ coverage on key services)
- ✅ API tests (50%+ coverage)
- ✅ LangSmith integration for agent debugging
- ✅ Structured logging (JSON format)
- ✅ Cost tracking (LLM usage logged)

**Documentation Requirements:**
- ✅ SPECS.md (this document)
- ✅ README.md (setup instructions, usage examples)
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Code comments and docstrings

**Deliverables:**
- Git repository with tagged v1.0.0 release
- Demo video (5-10 minutes)
- Capstone presentation slides

---

## 20. Risk Assessment

### 20.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AWS MCP servers unavailable | Medium | Fallback to vector-only, document workaround |
| LLM rate limits exceeded | High | Concurrency control, backoff retry, cost alerts |
| Qdrant performance issues | Medium | Optimize collection config, consider alternatives |
| LangGraph learning curve | Medium | Start simple, iterate, use LangSmith debugging |
| Time overrun (>60 hours) | High | Prioritize core workflows, defer UI polish |

### 20.2 Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM API costs higher than expected | Medium | Monitor daily, set budget alerts, optimize prompts |
| ECS deployment complexity | Low | Document thoroughly, test early |
| Data quality issues (seed data) | Low | Validate seed CSVs, add data quality checks |

### 20.3 Timeline Risk

**Critical Path:**
1. Database setup + migrations (4 hours)
2. Research workflow (12 hours)
3. Outreach workflow (8 hours)
4. Two-tier solution matching (8 hours)
5. API endpoints (6 hours)
6. Gradio UI (6 hours)
7. Testing (8 hours)
8. Deployment setup (4 hours)
9. Documentation (4 hours)

**Total Estimate:** 60 hours (upper bound)

**Buffer:** None built-in; defer optional features if needed

---

## 21. Glossary

- **MCP:** Model Context Protocol - standard for connecting LLMs to external data sources
- **LangGraph:** Framework for building stateful, multi-agent LLM workflows
- **LangSmith:** Observability platform for LangChain/LangGraph applications
- **ECS:** Amazon Elastic Container Service - managed container orchestration
- **RDS:** Amazon Relational Database Service - managed PostgreSQL
- **Qdrant:** Open-source vector database for semantic search
- **FastAPI:** Modern Python web framework for building APIs
- **Gradio:** Python library for building ML/AI web interfaces
- **Alembic:** Database migration tool for SQLAlchemy
- **Pydantic:** Data validation library using Python type annotations

---

## 22. References

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- LangSmith: https://smith.langchain.com
- FastAPI: https://fastapi.tiangolo.com
- Qdrant: https://qdrant.tech/documentation/
- AWS ECS: https://docs.aws.amazon.com/ecs/
- Gradio: https://gradio.app/docs/

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-15  
**Author:** Lefteris (with Claude assistance)  
**Status:** Approved for Implementation
# Sales Assistant Implementation Plan

## Task 1: Project Foundation & Configuration

### 1.1 Project Structure Setup

- [x] Create directory structure as per spec (app/, ui/, backend/, scripts/, data/, tests/, alembic/)
- [x] Initialize Git repository with proper .gitignore
- [x] Create requirements.txt for backend dependencies (pyproject.toml managed by uv)
- [ ] Create ui/requirements.txt for Gradio dependencies
- [x] Create .env.example template with all required environment variables
- [x] Verify structure matches spec section 16

### 1.2 Configuration Management

- [x] Implement app/config/settings.py with Pydantic BaseSettings
- [x] Add all environment variables from spec section 8.1
- [ ] Add validation for required settings
- [x] Test settings loading from .env file
- [x] Test settings validation (missing required fields should fail)

### 1.3 Logging Infrastructure

- [ ] Implement app/utils/logging.py with structured JSON logging
- [x] Configure log format per spec section 9.1
- [x] Add log level support (DEBUG, INFO, WARNING, ERROR)
- [ ] Implement log rotation (daily)
- [x] Test logging at different levels
- [x] Create logs/ directory (git-ignored)

---

## Task 2: Database Foundation

### 2.1 Database Models - Core Entities

- [x] Create app/models/database.py
- [x] Implement Prospect model (all fields from spec 3.1)
- [x] Implement Company model with JSONB fields
- [x] Implement AWSolution model
- [x] Implement ProspectResearch model
- [x] Implement Interaction model
- [x] Implement OutreachDraft model
- [x] Implement Event model
- [x] Implement LLMUsageLog model
- [ ] Test model instantiation with valid data

### 2.2 Database Models - Enums and Relationships

- [x] Define ProspectStatus enum
- [x] Define InteractionType enum
- [x] Define PricingModels enum
- [x] Add foreign key relationships (ProspectResearch → Prospect, etc.)
- [x] Add indexes per spec section 14.3
- [ ] Test relationship loading

### 2.3 Alembic Setup and Initial Migration

- [x] Initialize Alembic (alembic init alembic)
- [x] Configure alembic.ini with database connection
- [x] Update alembic/env.py to import models
- [x] Generate initial migration for all models
- [x] Test migration: alembic upgrade head
- [x] Test rollback: alembic downgrade -1
- [x] Document migration commands in README

### 2.4 Database CRUD Operations

- [x] Implement Prospect CRUD operations
- [x] Write unit tests for Prospect (18 tests)
- [x] Implement Company CRUD operations
- [x] Write unit tests for Company (19 tests)
- [x] Implement Solution (AWSolution) CRUD operations
- [x] Write unit tests for Solution (20 tests)
- [x] Implement ProspectResearch CRUD operations
- [x] Write unit tests for ProspectResearch (12 tests)
- [x] Implement Interaction CRUD operations
- [x] Implement OutreachDraft CRUD operations
- [x] Implement Event CRUD operations
- [x] Implement LLMUsageLog logging function
- [x] Write unit tests for remaining models (26 tests)
- [x] Verify all tests pass (95/95 ✅)
- [x] Create comprehensive documentation

---

## Task 3: Vector Store Infrastructure

### 3.1 pgvector Initialization

- [x] Create scripts/init_pgvector.py -> Add into create_database
- [x] Enable pgvector extension in PostgreSQL
- [x] Create solution_vectors table (dimension=384, ivfflat index)
- [x] Create interaction_vectors table
- [x] Add error handling for existing tables
- [x] Test script execution against local PostgreSQL
- [x] Add alembic upgrade for vector tables
- [ ] Document pgvector setup in README

### 3.2 Vector Service - Basic Operations

- [x] Create app/services/vector_service.py
- [x] Implement embedding generation using sentence-transformers (all-MiniLM-L12-v2)
- [x] Implement vector CRUD Operations for aws_solution_vectors table
- [x] Implement vector CRUD Operations for communication_vectors table
- [x] Add database session management
- [x] Test embedding generation (dimension check)
- [x] Write unit tests (tests/unit/services/test_vector_service.py)

### 3.3 Vector Service - Search Operations

- [x] Implement search_solutions() with filters (industry, keywords)
- [x] Implement search_communications_by_date()
- [ ] Add pagination support
- [x] Add similarity threshold parameter
- [x] Test search with various queries
- [x] Test filter combinations
- [x] Add tests for edge cases (empty results, invalid filters)

---

## Task 4: Seed Data Generation

### 4.1 AWS Solutions Seed Data

- [x] Create data/seeds/aws_solutions.csv template -> Single script for all data load_seed_data.py
- [x] Generate 30-50 AWS solution entries (use LLM or manual)
- [x] Include fields: name, category, description, use_cases, industries, keywords, pricing_model
- [x] Validate CSV formaly
- [x] Implement CSV parsing and PostgreSQL insertion
- [x] Test seeding script execution
- [x] Verify data in PostgreSQL

### 4.2 Vector Population for AWS Solutions

- [x] Create scripts/populate_vectors.py
- [x] Load AWS solutions from PostgreSQL
- [x] Generate embeddings for each solution
- [x] Insert into aws_solution_vectors table
- [x] Add progress logging
- [x] Test script execution
- [x] Verify vectors in PostgreSQL (count, sample search using pgvector)

### 4.3 Test Prospects Seed Data

- [x] Create data/seeds/test_prospects.csv -> Single script for all data load_seed_data.py
- [x] Generate 10-15 realistic prospect entries
- [x] Include: linkedin_url, full_name, title, company_name, industry, location
- [x] Ensure diverse industries and company sizes
- [x] Document CSV format for prospect imports

---

## Task 5: API Foundation

### 5.1 Pydantic API Models

- [x] Create app/models/api.py
- [x] Implement ProspectCreate schema
- [x] Implement ProspectUpdate schema
- [x] Implement SolutionCreate schema
- [x] Implement SolutionUpdate schema
- [x] Implement EventCreate schema
- [x] Implement EventUpdate schema
- [x] Implement CompanyCreate schema
- [x] Implement CompanyUpdate schema
- [x] Implement ProspectResponse schema
- [x] Implement CompanyResponse schema
- [x] Implement ResearchResponse schema
- [x] Implement InteractionCreate, InteractionUpdate, InteractionResponse schemas
- [x] Implement OutreachDraftCreate, OutreachDraftUpdate, OutreachDraftResponse schema
- [x] Implement EventResponse schema
- [ ] Test schema validation with valid/invalid data

### 5.2 FastAPI Application Setup

- [ ] Create app/main.py with FastAPI app instance
- [ ] Configure CORS middleware
- [ ] Add request logging middleware
- [ ] Add error handling middleware
- [ ] Implement /health endpoint
- [ ] Test app startup
- [ ] Test /health endpoint returns 200

### 5.3 API Routes - Prospects

- [ ] Create app/api/routes.py
- [ ] Implement POST /api/v1/prospects
- [ ] Implement GET /api/v1/prospects (with pagination)
- [ ] Implement GET /api/v1/prospects/{prospect_id}
- [ ] Implement PATCH /api/v1/prospects/{prospect_id}
- [ ] Add input validation and error responses (404, 400)
- [ ] Write API tests (tests/api/test_prospects_endpoints.py)
- [ ] Test all endpoints with curl

### 5.4 API Routes - CSV Import

- [ ] Implement GET /api/v1/prospects/import/template
- [ ] Implement POST /api/v1/prospects/import/csv
- [ ] Add CSV parsing with validation
- [ ] Add error handling for malformed CSV
- [ ] Return import summary (success count, errors)
- [ ] Test with valid CSV
- [ ] Test with invalid CSV (error handling)

---

## Task 6: Solution Matching - Tier 1 (Vector Only)

### 6.1 Solution Matcher Service Setup

- [ ] Create app/services/solution_matcher.py
- [ ] Implement SolutionMatcher class
- [ ] Add dependency injection for vector_service and database
- [ ] Implement context building from prospect + company data
- [ ] Test context building with sample data

### 6.2 Tier 1 Vector Search Implementation

- [ ] Implement search_aws_solutions() using vector_service
- [ ] Add industry filtering
- [ ] Add keyword filtering
- [ ] Return top 10 candidates
- [ ] Implement reference architecture search (top 3)
- [ ] Implement past communications search (top 5)
- [ ] Test with various prospect contexts
- [ ] Write unit tests (tests/unit/services/test_solution_matcher.py)

### 6.3 Solution Matcher Integration

- [ ] Implement match_solutions_for_prospect() orchestration method
- [ ] Combine aws_solutions + reference_architectures + past_communications
- [ ] Format response according to spec
- [ ] Add performance logging (< 500ms target)
- [ ] Test end-to-end matching
- [ ] Test with empty vector store (edge case)

---

## Task 7: AWS MCP Service (Tier 2)

### 7.1 MCP Service Setup

- [ ] Create app/services/aws_mcp_service.py
- [ ] Implement MCPService class
- [ ] Add configuration for MCP server URLs
- [ ] Implement connection/session management
- [ ] Add timeout configuration (5s default)
- [ ] Test connection to MCP servers (or mock if unavailable)

### 7.2 MCP Enrichment Implementation

- [ ] Implement enrich_solution() for single solution
- [ ] Query MCP for latest documentation
- [ ] Query MCP for pricing information
- [ ] Query MCP for compliance/region compatibility
- [ ] Format enriched response
- [ ] Test with mock MCP responses

### 7.3 MCP Batch Processing and Caching

- [ ] Implement enrich_solutions() for batch (top 5)
- [ ] Add in-memory cache (TTL: 24 hours)
- [ ] Implement cache key generation (solution_name:usage_pattern_hash)
- [ ] Add fallback to original data on MCP failure
- [ ] Test caching behavior
- [ ] Test fallback mechanism
- [ ] Write unit tests

### 7.4 Two-Tier Integration

- [ ] Update SolutionMatcher to use MCPService
- [ ] Implement degradation flag (mcp_unavailable: true)
- [ ] Add logging for tier switching
- [ ] Test full two-tier flow
- [ ] Test degradation (MCP down, returns Tier 1 only)

---

## Task 8: LangGraph - Research Workflow

### 8.1 Research Workflow State and Graph Setup

- [ ] Create app/agents/research_workflow.py
- [ ] Define ResearchState TypedDict per spec 5.1
- [ ] Create StateGraph instance
- [ ] Add all nodes (gather_context, research_company, etc.)
- [ ] Define node sequence/edges
- [ ] Compile graph
- [ ] Test graph compilation

### 8.2 Node: gather_context

- [ ] Implement gather_context node
- [ ] Load prospect from database
- [ ] Load company from database (or create if missing)
- [ ] Load manual_context from input
- [ ] Update state with loaded data
- [ ] Test node execution with mock state
- [ ] Add error handling for missing prospect

### 8.3 Node: research_company (Placeholder)

- [ ] Implement research_company node (placeholder: return mock data)
- [ ] Define input/output contract
- [ ] Add state update logic
- [ ] Test node with placeholder data
- [ ] Add logging

### 8.4 Node: analyze_tech_stack (Placeholder)

- [ ] Implement analyze_tech_stack node (placeholder)
- [ ] Define expected tech_stack_analysis structure
- [ ] Update state
- [ ] Test node

### 8.5 Node: identify_pain_points (Placeholder)

- [ ] Implement identify_pain_points node (placeholder)
- [ ] Define pain_points list structure
- [ ] Update state
- [ ] Test node

### 8.6 Node: match_solutions

- [ ] Implement match_solutions node
- [ ] Call SolutionMatcher.match_solutions_for_prospect()
- [ ] Update state with recommended_solutions and reference_architectures
- [ ] Test with real solution matcher
- [ ] Add error handling

### 8.7 Node: synthesize_research (Placeholder)

- [ ] Implement synthesize_research node (placeholder)
- [ ] Generate research_summary from state
- [ ] Calculate confidence_score (placeholder: 0.7)
- [ ] Collect sources
- [ ] Update state
- [ ] Test node

### 8.8 Research Workflow Execution and Persistence

- [ ] Implement workflow execution function
- [ ] Add input validation
- [ ] Execute graph with input state
- [ ] Save final state to ProspectResearch table
- [ ] Save intermediate states to JSON file (logs/research_traces/)
- [ ] Add LLM usage logging (placeholder)
- [ ] Test full workflow execution (end-to-end with placeholders)
- [ ] Write integration test (tests/integration/test_research_workflow.py)

### 8.9 Research Workflow - Add LLM Integration

- [ ] Add LangChain LLM provider initialization
- [ ] Update research_company node with real LLM call
- [ ] Update analyze_tech_stack node with real LLM call
- [ ] Update identify_pain_points node with real LLM call
- [ ] Update synthesize_research node with real LLM call
- [ ] Add exponential backoff retry decorator
- [ ] Add prompt templates
- [ ] Test with real LLM API
- [ ] Add LLM usage logging to LLMUsageLog table

### 8.10 Research API Endpoint

- [ ] Add POST /api/v1/prospects/{prospect_id}/research endpoint
- [ ] Add GET /api/v1/prospects/{prospect_id}/research (list all)
- [ ] Add GET /api/v1/prospects/{prospect_id}/research/latest
- [ ] Trigger research workflow on POST
- [ ] Return research summary
- [ ] Add error handling (prospect not found, workflow failure)
- [ ] Write API tests (tests/api/test_research_endpoints.py)
- [ ] Test with curl

---

## Task 9: LangGraph - Outreach Generation Workflow

### 9.1 Outreach Workflow State and Graph Setup

- [ ] Create app/agents/outreach_workflow.py
- [ ] Define OutreachState TypedDict per spec 5.2
- [ ] Create StateGraph instance
- [ ] Add all nodes (load_context through refine_draft)
- [ ] Define node sequence
- [ ] Compile graph
- [ ] Test compilation

### 9.2 Node: load_context

- [ ] Implement load_context node
- [ ] Load prospect, company, research from database
- [ ] Load event if event_id provided
- [ ] Load custom_context from input
- [ ] Update state
- [ ] Test node
- [ ] Add error handling (missing research)

### 9.3 Node: analyze_similar_wins

- [ ] Implement analyze_similar_wins node
- [ ] Use vector_service to search past_communications
- [ ] Filter by similarity and outcome (successful)
- [ ] Update state with similar_communications
- [ ] Test with populated vector store
- [ ] Test with empty vector store

### 9.4 Nodes: Email Generation (Placeholders)

- [ ] Implement plan_email_strategy node (placeholder)
- [ ] Implement generate_subject node (placeholder)
- [ ] Implement generate_body node (placeholder: 150-200 words)
- [ ] Implement refine_draft node (placeholder)
- [ ] Test each node
- [ ] Define state updates

### 9.5 Outreach Workflow Execution and Persistence

- [ ] Implement workflow execution function
- [ ] Execute graph with input state
- [ ] Save draft to OutreachDraft table
- [ ] Include event_id reference if applicable
- [ ] Add logging
- [ ] Test full workflow (end-to-end with placeholders)

### 9.6 Outreach Workflow - Add LLM Integration

- [ ] Update plan_email_strategy with real LLM call
- [ ] Update generate_subject with real LLM call
- [ ] Update generate_body with real LLM call (enforce 150-200 words)
- [ ] Update refine_draft with real LLM call
- [ ] Add retry logic
- [ ] Test with real LLM API
- [ ] Add LLM usage logging

### 9.7 Outreach API Endpoints

- [ ] Add POST /api/v1/prospects/{prospect_id}/outreach
- [ ] Add GET /api/v1/prospects/{prospect_id}/outreach
- [ ] Add PATCH /api/v1/outreach/{draft_id} (for editing)
- [ ] Trigger outreach workflow on POST
- [ ] Return draft
- [ ] Write API tests (tests/api/test_outreach_endpoints.py)
- [ ] Test with curl

---

## Task 10: LangGraph - Event Matching Workflow

### 10.1 Event Matching Workflow Setup

- [ ] Create app/agents/event_matching_workflow.py
- [ ] Define EventMatchingState TypedDict per spec 5.3
- [ ] Create StateGraph
- [ ] Add all nodes
- [ ] Define sequence
- [ ] Compile graph
- [ ] Test compilation

### 10.2 Node: load_event

- [ ] Implement load_event node
- [ ] Load event from database
- [ ] Update state
- [ ] Test node
- [ ] Add error handling

### 10.3 Node: find_candidates

- [ ] Implement find_candidates node
- [ ] SQL query: filter by target_industries, target_roles
- [ ] Vector search: similarity to event description
- [ ] Combine results (dedup by prospect_id)
- [ ] Update state with candidate_prospects
- [ ] Test with various events
- [ ] Test with no matches

### 10.4 Node: score_relevance (Placeholder)

- [ ] Implement score_relevance node (placeholder: random 0-100)
- [ ] Define scoring logic structure
- [ ] Update state with scored_prospects
- [ ] Test node

### 10.5 Node: select_top_matches

- [ ] Implement select_top_matches node
- [ ] Filter: top 20 or score >= 70
- [ ] Sort by score descending
- [ ] Update state with top_matches
- [ ] Test filtering logic

### 10.6 Node: generate_invitations (Placeholder)

- [ ] Implement generate_invitations node (placeholder)
- [ ] For each top match, call outreach workflow
- [ ] Include event_id in outreach context
- [ ] Collect invitation_drafts
- [ ] Update state
- [ ] Test with mock outreach calls

### 10.7 Event Matching - Add LLM Integration

- [ ] Update score_relevance with real LLM scoring
- [ ] Add concurrency control (max 5 concurrent LLM calls)
- [ ] Add error handling (skip failed scores)
- [ ] Update generate_invitations to call real outreach workflow
- [ ] Test with real LLM
- [ ] Add LLM usage logging

### 10.8 Event API Endpoints

- [ ] Add POST /api/v1/events (create event)
- [ ] Add GET /api/v1/events (list)
- [ ] Add GET /api/v1/events/{event_id}
- [ ] Add POST /api/v1/events/{event_id}/match-prospects
- [ ] Trigger event matching workflow on POST
- [ ] Return matched prospects and invitation drafts
- [ ] Write API tests (tests/api/test_events_endpoints.py)
- [ ] Test with curl

---

## Task 11: Reference Architecture Search Agent

### 11.1 Agent Implementation

- [ ] Create app/agents/reference_architecture_search.py
- [ ] Implement standalone agent (not full workflow)
- [ ] Add web search integration
- [ ] Add AWS documentation site search
- [ ] Parse and extract architecture links
- [ ] Generate summaries
- [ ] Test with sample queries ("e-commerce architecture", "fintech AWS")

### 11.2 Integration Points

- [ ] Add optional call from research workflow (if needed)
- [ ] Add direct API endpoint (optional): GET /api/v1/solutions/reference-search
- [ ] Test integration with research workflow
- [ ] Document usage

---

## Task 12: Additional API Endpoints

### 12.1 AWS Solutions Endpoints

- [ ] Add GET /api/v1/solutions (list all)
- [ ] Add POST /api/v1/solutions (create - admin use)
- [ ] Add GET /api/v1/solutions/search (query parameters)
- [ ] Test endpoints
- [ ] Write API tests

### 12.2 Interactions Endpoints

- [ ] Add POST /api/v1/prospects/{prospect_id}/interactions
- [ ] Add GET /api/v1/prospects/{prospect_id}/interactions
- [ ] Test endpoints
- [ ] Write API tests

### 12.3 Metrics Endpoint

- [ ] Add GET /api/v1/metrics/llm-usage
- [ ] Query LLMUsageLog table
- [ ] Support date range filtering (start_date, end_date)
- [ ] Return aggregated statistics (total cost, tokens, calls by provider)
- [ ] Test with sample data
- [ ] Write API tests

---

## Task 13: Gradio UI

### 13.1 Gradio UI Setup

- [ ] Create ui/app.py
- [ ] Create ui/Dockerfile
- [ ] Create ui/requirements.txt
- [ ] Add environment variable for BACKEND_URL
- [ ] Test basic Gradio app launch

### 13.2 Tab: Workflow Execution

- [ ] Create "Workflow Execution" tab
- [ ] Add workflow dropdown (Research, Outreach, Event Matching)
- [ ] Add dynamic inputs based on workflow selection
- [ ] Add "Run Workflow" button
- [ ] Implement backend API calls
- [ ] Display JSON/formatted results
- [ ] Add error handling and display
- [ ] Test with all three workflows

### 13.3 Tab: View Results

- [ ] Create "View Results" tab
- [ ] Add prospect selector (dropdown or search)
- [ ] Add sub-tabs: Research Summary, Outreach Drafts, Interactions
- [ ] Fetch and display research summary
- [ ] Fetch and display outreach drafts (list, clickable)
- [ ] Fetch and display interactions
- [ ] Add "Download as PDF" button (optional/future)
- [ ] Add "Copy to clipboard" button
- [ ] Test data display

### 13.4 Tab: Upload Context

- [ ] Create "Upload Context" tab
- [ ] Add file uploader (CSV, TXT, DOCX, PDF)
- [ ] Add upload type selector (Prospects, Communication, Event)
- [ ] Implement CSV prospect import
- [ ] Implement communication upload (future: parse and store)
- [ ] Implement event upload (future: parse and store)
- [ ] Display upload status (success/error)
- [ ] Test CSV upload

### 13.5 Tab: Dashboard (Optional)

- [ ] Create "Dashboard" tab
- [ ] Display prospect count by status (bar chart)
- [ ] Display LLM usage summary (last 7 days)
- [ ] Display recent activity log
- [ ] Test dashboard with sample data

---

## Task 14: Testing Infrastructure

### 14.1 Test Configuration

- [ ] Create pytest.ini
- [ ] Create tests/conftest.py with fixtures
- [ ] Add database test fixtures (test DB setup/teardown)
- [ ] Add mock LLM fixtures
- [ ] Add mock vector store fixtures
- [ ] Test fixture functionality

### 14.2 Unit Tests - Services

- [ ] Complete tests/unit/services/test_vector_service.py
- [ ] Complete tests/unit/services/test_solution_matcher.py
- [ ] Complete tests/unit/services/test_database.py
- [ ] Add tests/unit/services/test_aws_mcp_service.py
- [ ] Run unit tests: pytest tests/unit/
- [ ] Check coverage: pytest --cov=app/services

### 14.3 API Tests

- [ ] Complete tests/api/test_prospects_endpoints.py
- [ ] Complete tests/api/test_research_endpoints.py
- [ ] Complete tests/api/test_outreach_endpoints.py
- [ ] Add tests/api/test_events_endpoints.py
- [ ] Add tests/api/test_solutions_endpoints.py
- [ ] Run API tests: pytest tests/api/
- [ ] Check coverage

### 14.4 Integration Tests (Optional)

- [ ] Add tests/integration/test_research_workflow.py (with mocked LLM)
- [ ] Add tests/integration/test_outreach_workflow.py
- [ ] Add tests/integration/test_event_matching_workflow.py
- [ ] Run integration tests: pytest tests/integration/
- [ ] Document decision to skip if time-constrained

### 14.5 Curl Test Scripts

- [ ] Create tests/api/curl_tests/ directory
- [ ] Create scripts/generate_curl_tests.py
- [ ] Generate curl scripts from OpenAPI schema (use LLM)
- [ ] Organize by endpoint group (prospects.sh, research.sh, etc.)
- [ ] Test curl scripts against running server
- [ ] Document usage in README

---

## Task 15: Docker and Deployment

### 15.1 Backend Dockerfile

- [ ] Create backend/Dockerfile
- [ ] Use Python 3.11+ base image
- [ ] Install dependencies from requirements.txt
- [ ] Copy app/ directory
- [ ] Expose port 8000
- [ ] Set CMD to run FastAPI with uvicorn
- [ ] Test docker build
- [ ] Test docker run locally

### 15.2 Docker Compose Setup

- [ ] Create docker-compose.yml
- [ ] Add backend service (build: ./backend)
- [ ] Add gradio-ui service (build: ./ui)
- [ ] Configure port mappings (8000, 7860)
- [ ] Add environment variables
- [ ] Configure host.docker.internal for PostgreSQL with pgvector
- [ ] Add volume for logs
- [ ] Test: docker-compose up
- [ ] Test: verify both services accessible

### 15.3 AWS ECS Task Definitions

- [ ] Create deployment/ecs-backend-task.json
- [ ] Configure CPU: 1024, Memory: 2048
- [ ] Add container definition with ECR image placeholder
- [ ] Add secrets from AWS Secrets Manager
- [ ] Add CloudWatch logs configuration
- [ ] Create deployment/ecs-ui-task.json (similar structure)
- [ ] Document task definitions

### 15.4 AWS Deployment Documentation

- [ ] Document ECR repository setup
- [ ] Document RDS PostgreSQL 15+ setup with pgvector extension
- [ ] Document Secrets Manager configuration
- [ ] Document ECS cluster creation
- [ ] Document service creation
- [ ] Document ALB setup
- [ ] Create deployment/deploy.sh script
- [ ] Test deployment steps (document any issues)

---

## Task 16: Documentation

### 16.1 README.md

- [ ] Create comprehensive README.md
- [ ] Add project overview
- [ ] Add prerequisites section
- [ ] Add local development setup (step-by-step)
- [ ] Add Docker setup instructions
- [ ] Add usage examples
- [ ] Add API documentation link
- [ ] Add testing instructions
- [ ] Add deployment instructions
- [ ] Add troubleshooting section

### 16.2 API Documentation

- [ ] Verify FastAPI auto-generated docs at /docs
- [ ] Verify ReDoc at /redoc
- [ ] Add docstrings to all endpoint functions
- [ ] Add request/response examples
- [ ] Test OpenAPI schema completeness

### 16.3 Code Documentation

- [ ] Add docstrings to all workflow nodes
- [ ] Add docstrings to service classes and methods
- [ ] Add inline comments for complex logic
- [ ] Document environment variables
- [ ] Document configuration options

### 16.4 Final Documentation Review

- [ ] Sync SPECS.md with final implementation
- [ ] Update any deviations from original spec
- [ ] Document known limitations
- [ ] Document future enhancements (nice-to-have)
- [ ] Create demo script/walkthrough

---

## Task 17: LangSmith Integration

### 17.1 LangSmith Configuration

- [ ] Add LANGCHAIN_TRACING_V2 to environment variables
- [ ] Add LANGCHAIN_API_KEY configuration
- [ ] Add LANGCHAIN_PROJECT configuration
- [ ] Test LangSmith connection
- [ ] Verify traces appear in dashboard

### 17.2 Tracing Enhancement

- [ ] Add custom trace names for workflows
- [ ] Add metadata to traces (prospect_id, workflow_type)
- [ ] Test trace visibility in LangSmith
- [ ] Document LangSmith usage

---

## Task 18: Final Integration and Testing

### 18.1 End-to-End Testing

- [ ] Import test prospects via CSV
- [ ] Run research workflow on test prospect
- [ ] Verify research saved to database
- [ ] Generate outreach for researched prospect
- [ ] Verify outreach draft created
- [ ] Create test event
- [ ] Run event matching workflow
- [ ] Verify invitations generated

### 18.2 Performance Testing

- [ ] Measure research workflow execution time
- [ ] Measure solution matching latency (target < 500ms for Tier 1)
- [ ] Test concurrent workflow executions
- [ ] Monitor LLM API rate limits
- [ ] Document performance metrics

### 18.3 Error Scenario Testing

- [ ] Test with missing prospect (404 errors)
- [ ] Test with invalid CSV format
- [ ] Test with vector index unavailable (fallback to full-text search)
- [ ] Test with MCP unavailable (degradation to Tier 1)
- [ ] Test with LLM API failure (retry logic)
- [ ] Test database connection failure
- [ ] Document error handling behavior

### 18.4 UI Testing

- [ ] Test all workflows from Gradio UI
- [ ] Test CSV upload from UI
- [ ] Test result viewing from UI
- [ ] Test error display in UI
- [ ] Test on different browsers (optional)
- [ ] Document any UI limitations

---

## Task 19: Capstone Deliverables

### 19.1 Code Repository

- [ ] Create clean git history
- [ ] Tag v1.0.0 release
- [ ] Push to GitHub/GitLab
- [ ] Ensure .gitignore excludes .env, logs/, etc.
- [ ] Verify all seed data included
- [ ] Verify all documentation included

### 19.2 Demo Video

- [ ] Script demo walkthrough (5-10 minutes)
- [ ] Record: import prospects
- [ ] Record: run research workflow
- [ ] Record: generate outreach
- [ ] Record: event matching
- [ ] Record: view results in UI
- [ ] Record: show LangSmith traces (optional)
- [ ] Edit and export video

### 19.3 Presentation Slides

- [ ] Create presentation deck
- [ ] Slide: Project overview
- [ ] Slide: Architecture diagram
- [ ] Slide: Technology stack
- [ ] Slide: Key workflows (Research, Outreach, Event Matching)
- [ ] Slide: Two-tier solution matching
- [ ] Slide: Demo screenshots
- [ ] Slide: Challenges and learnings
- [ ] Slide: Future enhancements
- [ ] Review and finalize

---

## Task 20: Optional Enhancements (Time Permitting)

### 20.1 Enhanced Error Messages

- [ ] Add user-friendly error messages in API responses
- [ ] Add validation error details
- [ ] Add suggestions for common errors

### 20.2 Performance Optimizations

- [ ] Add database query optimization
- [ ] Add connection pooling tuning
- [ ] Add async optimizations where applicable

### 20.3 Additional Features

- [ ] Add prospect status transitions (workflow: NEW → RESEARCHED → CONTACTED)
- [ ] Add bulk operations (batch research)
- [ ] Add export functionality (JSON, CSV downloads)

---

## Progress Tracking

**Total Tasks:** 20
**Completed:** 4
**In Progress:** 1
**Remaining:** 15

**Estimated Timeline:** 40-60 hours
**Target Completion:** v1.0.0 Capstone Submission

---

## Notes

- Tasks are ordered to build from primitives (database, vector store) to integrated features (workflows, UI)
- Each subtask is designed to be individually testable
- Testing subtasks are integrated throughout rather than deferred to the end
- Workflows are built incrementally: structure → placeholders → LLM integration
- Optional tasks (Task 20) can be skipped if time-constrained
- Regular commits recommended after completing each task section
- Use git branches for major features if preferred

# Database Schema Documentation

## Overview

This database schema supports a sales assistant application that manages prospects, companies, events, solutions, and outreach activities. The schema includes tracking for AI/LLM usage, research insights, and interaction history.

## Tables

### alembic_version

Database migration version tracking table (managed by Alembic).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| version_num | VARCHAR(32) | PRIMARY KEY, NOT NULL | Current migration version identifier |

---

### events

Stores information about sales events, conferences, and other business gatherings.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique event identifier |
| event_type | VARCHAR(255) | NOT NULL | Type/category of the event |
| event_date | TIMESTAMP | NOT NULL | Date and time of the event |
| description | TEXT | NOT NULL | Detailed event description |
| location | VARCHAR(255) | NOT NULL | Event location |
| target_industries | JSONB | | Industries targeted by this event |
| target_roles | JSONB | | Job roles/titles targeted by this event |
| solutions_featured | JSONB | | Solutions or products featured at the event |
| status | VARCHAR(255) | NOT NULL | Current event status |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

---

### industries

Master list of industry classifications.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique industry identifier |
| name | VARCHAR(255) | NOT NULL | Industry name |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

---

### llm_usage_logs

Tracks usage and performance metrics for LLM/AI operations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique log entry identifier |
| worfklow_name | VARCHAR(255) | NOT NULL | Name of the workflow using the LLM |
| node_name | VARCHAR(255) | NOT NULL | Specific node/step in the workflow |
| model | VARCHAR(255) | NOT NULL | LLM model identifier |
| prompt_tokens | INTEGER | NOT NULL | Number of tokens in the prompt |
| completion_tokens | INTEGER | NOT NULL | Number of tokens in the completion |
| total_tokens | INTEGER | NOT NULL | Total tokens used |
| latency_ms | INTEGER | NOT NULL | Response latency in milliseconds |
| cost | DOUBLE PRECISION | NOT NULL | Cost of the LLM operation |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

---

### solutions

Catalog of products, services, or solutions offered.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique solution identifier |
| name | VARCHAR(255) | NOT NULL | Solution name |
| category | VARCHAR(255) | NOT NULL | Solution category/type |
| description | TEXT | NOT NULL | Detailed solution description |
| use_cases | JSONB | | Common use cases for this solution |
| keywords | JSONB | | Keywords for search/matching |
| pricing_model | VARCHAR(255) | NOT NULL | Pricing structure |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

---

### companies

Organizations that prospects belong to.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique company identifier |
| name | VARCHAR(255) | NOT NULL | Company name |
| industry_id | INTEGER | NOT NULL, FOREIGN KEY → industries(id) | Associated industry |
| size | VARCHAR(255) | NOT NULL | Company size category |
| website | VARCHAR(255) | | Company website URL |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Foreign Keys:**
- `industry_id` → `industries(id)`

---

### industry_solutions

Junction table mapping industries to relevant solutions (many-to-many relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| industry_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY → industries(id) | Industry identifier |
| solution_id | INTEGER | PRIMARY KEY, NOT NULL, FOREIGN KEY → solutions(id) | Solution identifier |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Primary Key:** Composite key on (industry_id, solution_id)

**Foreign Keys:**
- `industry_id` → `industries(id)`
- `solution_id` → `solutions(id)`

---

### prospects

Individual contacts/leads for sales outreach.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique prospect identifier |
| full_name | VARCHAR(255) | NOT NULL | Prospect's full name |
| email | VARCHAR(255) | NOT NULL | Email address |
| linkedin_url | VARCHAR(255) | | LinkedIn profile URL |
| location | VARCHAR(255) | | Geographic location |
| company_id | INTEGER | NOT NULL, FOREIGN KEY → companies(id) | Associated company |
| last_contacted_at | TIMESTAMP | | Last contact timestamp |
| is_active | BOOLEAN | NOT NULL | Whether prospect is active |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Foreign Keys:**
- `company_id` → `companies(id)`

---

### interactions

History of all interactions with prospects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique interaction identifier |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) | Associated prospect |
| event_id | INTEGER | FOREIGN KEY → events(id) | Associated event (if applicable) |
| interaction_type | VARCHAR(255) | NOT NULL | Type of interaction |
| interaction_date | TIMESTAMP | NOT NULL | When the interaction occurred |
| subject | VARCHAR(255) | NOT NULL | Interaction subject/title |
| content | TEXT | NOT NULL | Full interaction content |
| sentiment | VARCHAR(255) | | Detected sentiment of interaction |
| outcome | TEXT | | Result or outcome of interaction |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Foreign Keys:**
- `prospect_id` → `prospects(id)`
- `event_id` → `events(id)`

---

### outreach_drafts

Drafts of outreach messages prepared for prospects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique draft identifier |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) | Target prospect |
| event_id | INTEGER | FOREIGN KEY → events(id) | Related event (if applicable) |
| draft_type | VARCHAR(255) | NOT NULL | Type of outreach message |
| content | TEXT | NOT NULL | Draft message content |
| status | VARCHAR(255) | NOT NULL | Draft status |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Foreign Keys:**
- `prospect_id` → `prospects(id)`
- `event_id` → `events(id)`

---

### prospect_research

AI-generated research and insights about prospects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY, NOT NULL | Unique research record identifier |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) | Associated prospect |
| research_summary | TEXT | NOT NULL | Summary of research findings |
| key_insights | JSONB | | Structured key insights |
| recommended_solutions | JSONB | | Solutions recommended for this prospect |
| confidence_score | DOUBLE PRECISION | | AI confidence score for recommendations |
| created_at | TIMESTAMP | NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Record last update timestamp |

**Foreign Keys:**
- `prospect_id` → `prospects(id)`

---

## Relationships

### One-to-Many Relationships

- **industries** → **companies**: One industry has many companies
- **companies** → **prospects**: One company has many prospects
- **prospects** → **interactions**: One prospect has many interactions
- **prospects** → **outreach_drafts**: One prospect has many outreach drafts
- **prospects** → **prospect_research**: One prospect has many research records
- **events** → **interactions**: One event can have many interactions
- **events** → **outreach_drafts**: One event can be referenced in many drafts

### Many-to-Many Relationships

- **industries** ↔ **solutions**: Through `industry_solutions` junction table

## JSONB Fields

Several tables use JSONB for flexible, semi-structured data:

- **events**: `target_industries`, `target_roles`, `solutions_featured`
- **solutions**: `use_cases`, `keywords`
- **prospect_research**: `key_insights`, `recommended_solutions`

## Audit Fields

All tables (except `alembic_version`) include standard audit timestamps:
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp

## ER Diagram
![ER diagram](schema.png)
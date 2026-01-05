# Database Schema Documentation

## Overview

This database schema supports a sales assistant application that manages prospects, companies, events, solutions, and related interactions. It includes vector embeddings for semantic search capabilities and LLM usage tracking.

---

## Tables

### alembic_version

Tracks database migration versions.

| Column | Type | Constraints |
|--------|------|-----------|
| version_num | VARCHAR(32) | PRIMARY KEY, NOT NULL |

---

### companies

Stores company information linked to industries.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| industry_id | INTEGER | NOT NULL, FOREIGN KEY → industries(id) |
| size | VARCHAR(255) | NOT NULL |
| website | VARCHAR(255) | |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### events

Records events such as conferences, webinars, or trade shows.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| event_type | VARCHAR(255) | NOT NULL |
| event_date | TIMESTAMP | NOT NULL |
| description | TEXT | NOT NULL |
| location | VARCHAR(255) | NOT NULL |
| target_industries | JSONB | |
| target_roles | JSONB | |
| solutions_featured | JSONB | |
| status | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### industries

Master list of industry classifications.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### industry_solutions

Junction table linking industries to solutions.

| Column | Type | Constraints |
|--------|------|-----------|
| industry_id | INTEGER | PRIMARY KEY, FOREIGN KEY → industries(id) |
| solution_id | INTEGER | PRIMARY KEY, FOREIGN KEY → solutions(id) |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### interactions

Logs interactions with prospects (emails, calls, meetings, etc.).

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) |
| event_id | INTEGER | FOREIGN KEY → events(id) |
| interaction_type | interaction_types | NOT NULL |
| interaction_date | TIMESTAMP | NOT NULL |
| subject | VARCHAR(255) | NOT NULL |
| content | TEXT | NOT NULL |
| sentiment | VARCHAR(255) | |
| outcome | TEXT | |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### interaction_vectors

Vector embeddings for interactions, enabling semantic search.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| interaction_id | INTEGER | NOT NULL, FOREIGN KEY → interactions(id) |
| embedding | VECTOR(384) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### llm_usage_logs

Tracks LLM API usage and costs for monitoring and analytics.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| worfklow_name | VARCHAR(255) | NOT NULL |
| node_name | VARCHAR(255) | NOT NULL |
| model | VARCHAR(255) | NOT NULL |
| prompt_tokens | INTEGER | NOT NULL |
| completion_tokens | INTEGER | NOT NULL |
| total_tokens | INTEGER | NOT NULL |
| latency_ms | INTEGER | NOT NULL |
| cost | DOUBLE PRECISION | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### outreach_drafts

Stores draft outreach messages to prospects.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) |
| event_id | INTEGER | FOREIGN KEY → events(id) |
| draft_type | VARCHAR(255) | NOT NULL |
| content | TEXT | NOT NULL |
| status | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### prospect_research

Stores research data and insights for prospects.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| prospect_id | INTEGER | NOT NULL, FOREIGN KEY → prospects(id) |
| research_summary | TEXT | NOT NULL |
| key_insights | JSONB | |
| recommended_solutions | JSONB | |
| confidence_score | DOUBLE PRECISION | |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### prospects

Stores individual prospect/contact information.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| full_name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | NOT NULL |
| linkedin_url | VARCHAR(255) | |
| location | VARCHAR(255) | |
| company_id | INTEGER | NOT NULL, FOREIGN KEY → companies(id) |
| last_contacted_at | TIMESTAMP | |
| is_active | BOOLEAN | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| status | prospect_status | NOT NULL |

---

### solutions

Master list of solutions offered.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| category | VARCHAR(255) | NOT NULL |
| description | TEXT | NOT NULL |
| use_cases | JSONB | |
| keywords | JSONB | |
| pricing_model | pricing_models | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

### solution_vectors

Vector embeddings for solutions, enabling semantic search and recommendations.

| Column | Type | Constraints |
|--------|------|-----------|
| id | SERIAL | PRIMARY KEY |
| solution_id | INTEGER | NOT NULL, FOREIGN KEY → solutions(id) |
| embedding | VECTOR(384) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

## Custom Types

- **interaction_types**: Enum for interaction classification (e.g., email, call, meeting)
- **pricing_models**: Enum for solution pricing models
- **prospect_status**: Enum for prospect lifecycle status

---

## Relationships

```
industries
├── companies (1-to-many)
├── industry_solutions (many-to-many via solutions)
└── prospects (indirect via companies)

companies
└── prospects (1-to-many)

solutions
├── industry_solutions (many-to-many via industries)
└── solution_vectors (1-to-many)

prospects
├── interactions (1-to-many)
├── outreach_drafts (1-to-many)
└── prospect_research (1-to-one)

events
├── interactions (1-to-many)
└── outreach_drafts (1-to-many)

interactions
└── interaction_vectors (1-to-many)
```

---

## Key Features

- **Vector Search**: Solution and interaction embeddings (384-dimensional) for semantic search
- **Event Tracking**: Comprehensive event management with JSONB fields for flexible target audience and solution associations
- **Interaction History**: Complete audit trail of prospect interactions with sentiment analysis
- **Research & Analytics**: Prospect research summaries and LLM usage tracking for cost monitoring
- **Flexible Data Storage**: JSONB columns for storing semi-structured data (use cases, insights, keywords)

## ER Diagram

![ER Diagram](schema.png)

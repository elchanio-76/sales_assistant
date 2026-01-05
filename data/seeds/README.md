# Seed Data for Sales Assistant Database

This directory contains CSV files with seed data for populating the test database.

## Generated Files

### 1. test_industries.csv (5 industries)
- Financial Services
- Healthcare & Life Sciences
- Manufacturing & Industrial
- Energy & Utilities
- Retail & E-commerce

### 2. test_companies.csv (5 companies)
Each company includes:
- name
- industry_id (foreign key to industries)
- size (employee count range)
- website (fictitious .example.com domains)

Companies:
1. GlobalBank Solutions (Financial Services)
2. MediTech Innovations (Healthcare)
3. Precision Manufacturing Co (Manufacturing)
4. GreenPower Energy (Energy)
5. NextGen Retail Group (Retail)

### 3. test_prospects.csv (20 prospects)
Each prospect includes:
- full_name
- email (company domain)
- linkedin_url (fictitious LinkedIn profiles)
- location (US cities)
- company_id (foreign key to companies)
- status (NEW, RESEARCHED, CONTACTED, ENGAGED, QUALIFIED)
- is_active (TRUE/FALSE)
- last_contacted_at (recent dates for contacted prospects)

Prospects are distributed across all 5 companies with various statuses and roles including:
- CTOs, CIOs, VPs of Engineering
- DevOps Engineers, Cloud Architects
- Data Scientists, ML Engineers
- Security Specialists, IT Directors

### 4. test_solutions.csv (20 AWS solutions)
Each solution includes:
- name (AWS service name)
- category (Compute, Storage, Databases, Observability, Security)
- description (3-4 sentence detailed description)
- use_cases (JSON array of common use cases)
- keywords (JSON array of relevant keywords)
- pricing_model (ON_DEMAND or SUBSCRIPTION)

#### Solutions by Category:

**Compute (6):**
- Amazon EC2 - Intel
- Amazon EC2 - Graviton
- AWS Lambda
- Amazon ECS
- Amazon EKS
- AWS Fargate

**Storage (4):**
- Amazon S3 Standard
- Amazon S3 Intelligent-Tiering
- Amazon EBS
- Amazon EFS

**Databases (5):**
- Amazon RDS MySQL
- Amazon DynamoDB
- Amazon DocumentDB
- Amazon Aurora MySQL
- Amazon Aurora PostgreSQL

**Observability (2):**
- Amazon CloudWatch
- AWS CloudTrail

**Security (3):**
- AWS KMS
- AWS IAM
- AWS Shield Advanced

## Data Characteristics

### Realistic but Fictitious
- All names, emails, and URLs are fictitious using .example.com domains
- LinkedIn URLs follow realistic patterns but are not real profiles
- Email addresses match company domains
- Locations are real US cities
- Job titles and roles are realistic for enterprise technology organizations

### Relationships
- Industries (5) → Companies (5) → Prospects (20)
- Each company belongs to one industry
- Prospects are distributed across companies (4 per company)
- Solutions are independent but can be linked via IndustrySolution table

### Data Distribution
- Prospect Status: Mix of NEW, RESEARCHED, CONTACTED, ENGAGED, QUALIFIED
- Company Sizes: Range from 500-1000 to 10000+ employees
- Locations: Distributed across major US tech hubs and industry centers
- Pricing Models: Primarily ON_DEMAND with one SUBSCRIPTION (Shield Advanced)

## Usage

These CSV files can be loaded into the database using:
1. Python scripts with pandas
2. PostgreSQL COPY commands
3. Database migration tools
4. Custom seed data loaders

## Notes

- All timestamps use ISO 8601 format
- Boolean values are uppercase (TRUE/FALSE)
- JSON fields (use_cases, keywords) use proper JSON array syntax
- Foreign keys reference the id column of parent tables (1-indexed)

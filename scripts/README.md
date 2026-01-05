# Scripts Directory

This directory contains utility scripts for database management and data loading.

## Seed Data Scripts

### load_seed_data.py

Loads seed data from CSV files into the database.

**Usage:**
```bash
# Load seed data (preserves existing data, skips duplicates)
python scripts/load_seed_data.py

# Clear existing seed data and reload (DESTRUCTIVE)
python scripts/load_seed_data.py --clear
```

**Features:**
- ✓ Idempotent: Skips existing records, only adds new ones
- ✓ Maintains referential integrity (loads in correct order)
- ✓ Validates data before insertion
- ✓ Parses JSON fields for solutions (use_cases, keywords)
- ✓ Converts enum strings to proper enum values
- ✓ Detailed logging with progress indicators
- ✓ Error handling with rollback on failure

**Data Loading Order:**
1. Industries (5 records)
2. Companies (5 records) - References industries
3. Prospects (20 records) - References companies
4. Solutions (20 records) - Independent

**CSV Files Location:**
`data/seeds/test_*.csv`

### verify_seed_data.py

Verifies seed data in the database and displays summary information.

**Usage:**
```bash
python scripts/verify_seed_data.py
```

**Output:**
- Record counts for all tables
- Sample records from each table
- Solutions grouped by category
- Relationship verification (companies → industries, prospects → companies)

## Other Scripts

### extract_ddl.py
Extracts DDL (Data Definition Language) from the database.

### document_db.sh
Shell script for database documentation tasks.

## Development Workflow

### Initial Setup
```bash
# 1. Run database migrations
alembic upgrade head

# 2. Load seed data
python scripts/load_seed_data.py

# 3. Verify data was loaded
python scripts/verify_seed_data.py
```

### Reset and Reload
```bash
# Clear and reload all seed data
python scripts/load_seed_data.py --clear
```

### Update Seed Data
```bash
# 1. Edit CSV files in data/seeds/
# 2. Run load script (it will skip existing records)
python scripts/load_seed_data.py
```

## Notes

- All scripts add the project root to Python path automatically
- Scripts use the existing CRUD operations from `app/services/db_crud.py`
- Database connection uses settings from `.env` file
- Seed data uses fictitious `.example.com` domains for safety
- JSON fields in CSVs must use proper JSON array syntax

## Error Handling

If the load script fails:
1. Check database connection (`.env` settings)
2. Verify CSV files exist and are properly formatted
3. Check logs for specific error messages
4. Ensure database schema is up to date (`alembic upgrade head`)

The script will rollback any partial changes on error.

#!/usr/bin/env python3
"""
Load seed data from CSV files into the database.

This script reads CSV files from data/seeds/ and populates the database
with industries, companies, prospects, and solutions.

Usage:
    python scripts/load_seed_data.py [--clear]

Options:
    --clear    Clear existing seed data before loading (WARNING: Destructive)
"""

import sys
import os
import argparse
import logging
from pathlib import Path
import csv
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import (
    Industry,
    Company,
    Prospect,
    Solution,
    ProspectStatus,
    PricingModels,
)
from app.services.db_crud import (
    get_db_session,
    create_or_update_company,
    create_or_update_prospect,
    create_or_update_solution,
)
from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths to seed data files
SEEDS_DIR = project_root / "data" / "seeds"
INDUSTRIES_CSV = SEEDS_DIR / "test_industries.csv"
COMPANIES_CSV = SEEDS_DIR / "test_companies.csv"
PROSPECTS_CSV = SEEDS_DIR / "test_prospects.csv"
SOLUTIONS_CSV = SEEDS_DIR / "test_solutions.csv"


def clear_seed_data():
    """Clear all seed data from the database (DESTRUCTIVE)."""
    logger.warning("Clearing existing seed data...")

    with get_db_session() as session:
        try:
            # Delete in reverse order of dependencies
            session.query(Prospect).delete()
            session.query(Company).delete()
            session.query(Industry).delete()
            session.query(Solution).delete()

            session.commit()
            logger.info("✓ Seed data cleared successfully")
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Error clearing seed data: {e}")
            raise


def load_industries():
    """Load industries from CSV."""
    logger.info(f"Loading industries from {INDUSTRIES_CSV}...")

    industries_created = 0
    total_rows = 0

    with open(INDUSTRIES_CSV, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)

        with get_db_session() as session:
            for row in rows:
                # Check if industry already exists
                existing = session.query(Industry).filter(
                    Industry.name == row['name']
                ).first()

                if existing:
                    logger.info(f"  - Industry '{row['name']}' already exists (id={existing.id})")
                    continue

                # Create new industry
                industry = Industry(name=row['name'])
                session.add(industry)
                session.flush()  # Flush to get the ID
                industries_created += 1
                logger.info(f"  + Created industry: {industry.name} (id={industry.id})")

            session.commit()

    logger.info(f"✓ Industries loaded: {industries_created} created, {total_rows - industries_created} existed")
    return total_rows


def load_companies():
    """Load companies from CSV."""
    logger.info(f"Loading companies from {COMPANIES_CSV}...")

    companies_created = 0
    total_rows = 0

    with open(COMPANIES_CSV, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)

        with get_db_session() as session:
            for row in rows:
                # Check if company already exists
                existing = session.query(Company).filter(
                    Company.name == row['name']
                ).first()

                if existing:
                    logger.info(f"  - Company '{row['name']}' already exists (id={existing.id})")
                    continue

                # Create new company
                company = Company(
                    name=row['name'],
                    industry_id=int(row['industry_id']),
                    size=row['size'],
                    website=row['website'] if row['website'].strip() else None
                )
                session.add(company)
                session.flush()
                companies_created += 1
                logger.info(f"  + Created company: {company.name} (id={company.id})")

            session.commit()

    logger.info(f"✓ Companies loaded: {companies_created} created, {total_rows - companies_created} existed")
    return total_rows


def load_prospects():
    """Load prospects from CSV."""
    logger.info(f"Loading prospects from {PROSPECTS_CSV}...")

    prospects_created = 0
    total_rows = 0

    with open(PROSPECTS_CSV, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)

        with get_db_session() as session:
            for row in rows:
                # Check if prospect already exists (by email)
                existing = session.query(Prospect).filter(
                    Prospect.email == row['email']
                ).first()

                if existing:
                    logger.info(f"  - Prospect '{row['full_name']}' already exists (id={existing.id})")
                    continue

                # Parse last_contacted_at
                last_contacted = None
                if row['last_contacted_at'].strip():
                    try:
                        last_contacted = datetime.fromisoformat(row['last_contacted_at'])
                    except ValueError:
                        logger.warning(f"  ! Invalid date format for {row['full_name']}: {row['last_contacted_at']}")

                # Create new prospect
                prospect = Prospect(
                    full_name=row['full_name'],
                    email=row['email'],
                    linkedin_url=row['linkedin_url'] if row['linkedin_url'].strip() else None,
                    location=row['location'] if row['location'].strip() else None,
                    company_id=int(row['company_id']),
                    status=ProspectStatus[row['status']],  # Convert string to enum
                    is_active=row['is_active'].upper() == 'TRUE',
                    last_contacted_at=last_contacted
                )
                session.add(prospect)
                session.flush()
                prospects_created += 1
                logger.info(f"  + Created prospect: {prospect.full_name} ({prospect.status.value}) (id={prospect.id})")

            session.commit()

    logger.info(f"✓ Prospects loaded: {prospects_created} created, {total_rows - prospects_created} existed")
    return total_rows


def load_solutions():
    """Load solutions from CSV."""
    logger.info(f"Loading solutions from {SOLUTIONS_CSV}...")

    solutions_created = 0
    total_rows = 0

    with open(SOLUTIONS_CSV, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        total_rows = len(rows)

        with get_db_session() as session:
            for row in rows:
                # Check if solution already exists
                existing = session.query(Solution).filter(
                    Solution.name == row['name']
                ).first()

                if existing:
                    logger.info(f"  - Solution '{row['name']}' already exists (id={existing.id})")
                    continue

                # Parse JSON fields
                use_cases = None
                keywords = None

                try:
                    if row['use_cases'].strip():
                        use_cases = json.loads(row['use_cases'])
                except json.JSONDecodeError as e:
                    logger.warning(f"  ! Invalid JSON for use_cases in {row['name']}: {e}")

                try:
                    if row['keywords'].strip():
                        keywords = json.loads(row['keywords'])
                except json.JSONDecodeError as e:
                    logger.warning(f"  ! Invalid JSON for keywords in {row['name']}: {e}")

                # Create new solution
                solution = Solution(
                    name=row['name'],
                    category=row['category'],
                    description=row['description'],
                    use_cases=use_cases,
                    keywords=keywords,
                    pricing_model=PricingModels[row['pricing_model']]  # Convert string to enum
                )
                session.add(solution)
                session.flush()
                solutions_created += 1
                logger.info(f"  + Created solution: {solution.name} ({solution.category}) (id={solution.id})")

            session.commit()

    logger.info(f"✓ Solutions loaded: {solutions_created} created, {total_rows - solutions_created} existed")
    return total_rows


def main():
    """Main function to load all seed data."""
    parser = argparse.ArgumentParser(
        description='Load seed data into the database',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing seed data before loading (WARNING: Destructive)'
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Starting seed data load process")
    logger.info("=" * 60)

    # Verify all CSV files exist
    missing_files = []
    for csv_file in [INDUSTRIES_CSV, COMPANIES_CSV, PROSPECTS_CSV, SOLUTIONS_CSV]:
        if not csv_file.exists():
            missing_files.append(csv_file)

    if missing_files:
        logger.error("Missing CSV files:")
        for file in missing_files:
            logger.error(f"  - {file}")
        sys.exit(1)

    try:
        # Clear existing data if requested
        if args.clear:
            response = input("⚠️  WARNING: This will delete all existing seed data. Continue? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Operation cancelled")
                return
            clear_seed_data()
            logger.info("")

        # Load data in order of dependencies
        total_industries = load_industries()
        logger.info("")

        total_companies = load_companies()
        logger.info("")

        total_prospects = load_prospects()
        logger.info("")

        total_solutions = load_solutions()
        logger.info("")

        # Summary
        logger.info("=" * 60)
        logger.info("Seed data load complete!")
        logger.info("=" * 60)
        logger.info(f"Industries: {total_industries}")
        logger.info(f"Companies:  {total_companies}")
        logger.info(f"Prospects:  {total_prospects}")
        logger.info(f"Solutions:  {total_solutions}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"✗ Error loading seed data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

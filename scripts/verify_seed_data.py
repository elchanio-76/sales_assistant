#!/usr/bin/env python3
"""
Verify seed data in the database.

This script queries the database to show counts and sample records
from the seed data tables.

Usage:
    python scripts/verify_seed_data.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.models.database import Industry, Company, Prospect, Solution
from app.services.db_crud import get_db_session


def verify_data():
    """Verify seed data in the database."""
    print("=" * 70)
    print("DATABASE SEED DATA VERIFICATION")
    print("=" * 70)
    print()

    with get_db_session() as session:
        # Count records
        industry_count = session.query(Industry).count()
        company_count = session.query(Company).count()
        prospect_count = session.query(Prospect).count()
        solution_count = session.query(Solution).count()

        # Summary
        print("📊 RECORD COUNTS:")
        print(f"  Industries: {industry_count}")
        print(f"  Companies:  {company_count}")
        print(f"  Prospects:  {prospect_count}")
        print(f"  Solutions:  {solution_count}")
        print()

        # Show sample industries
        if industry_count > 0:
            print("🏢 INDUSTRIES:")
            industries = session.query(Industry).limit(5).all()
            for ind in industries:
                print(f"  [{ind.id}] {ind.name}")
            print()

        # Show sample companies
        if company_count > 0:
            print("🏭 COMPANIES:")
            companies = session.query(Company).limit(5).all()
            for comp in companies:
                industry = session.query(Industry).filter(
                    Industry.id == comp.industry_id
                ).first()
                print(f"  [{comp.id}] {comp.name} ({industry.name if industry else 'Unknown'}) - {comp.size} employees")
            print()

        # Show sample prospects
        if prospect_count > 0:
            print("👥 PROSPECTS (Sample):")
            prospects = session.query(Prospect).limit(5).all()
            for pros in prospects:
                company = session.query(Company).filter(
                    Company.id == pros.company_id
                ).first()
                print(f"  [{pros.id}] {pros.full_name} ({pros.status.value}) @ {company.name if company else 'Unknown'}")
            print()

        # Show solutions by category
        if solution_count > 0:
            print("💡 SOLUTIONS BY CATEGORY:")
            categories = session.query(Solution.category).distinct().all()
            for (category,) in categories:
                count = session.query(Solution).filter(
                    Solution.category == category
                ).count()
                print(f"  {category}: {count} solutions")

                # Show solutions in this category
                solutions = session.query(Solution).filter(
                    Solution.category == category
                ).limit(3).all()
                for sol in solutions:
                    print(f"    - {sol.name} ({sol.pricing_model.value})")
            print()

        # Summary
        print("=" * 70)
        if industry_count == 0 and company_count == 0 and prospect_count == 0 and solution_count == 0:
            print("⚠️  No seed data found. Run 'python scripts/load_seed_data.py' to load data.")
        else:
            print("✓ Seed data verification complete!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        verify_data()
    except Exception as e:
        print(f"✗ Error verifying seed data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

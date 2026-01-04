"""
Unit tests for Company CRUD operations using PostgreSQL.

Following the same pattern as test_db_crud_improved.py for Prospect model.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import sys
import os

# Add app directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from app.models.database import Base, Company, Industry
import app.services.db_crud as crud


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sales_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a PostgreSQL test database engine.

    This fixture:
    - Uses the existing test database (created by migrations)
    - Does NOT drop tables (preserves migration history)
    - Only truncates data between test runs
    """
    # Create engine for test database
    engine = create_engine(TEST_DATABASE_URL, echo=False)

    yield engine

    # Minimal cleanup - just truncate tables, don't drop them
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # End any open transaction

        # Get all table names except alembic_version
        result = conn.execute(
            text(
                """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename != 'alembic_version'
        """
            )
        )

        tables = [row[0] for row in result]

        if tables:
            # Truncate all tables (CASCADE handles foreign keys)
            tables_str = ", ".join(tables)
            conn.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"))
            conn.execute(text("COMMIT"))

    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_db_engine):
    """
    Create a test database session with transaction rollback.

    Each test runs in a transaction that's rolled back after the test,
    ensuring test isolation without dropping tables.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def sample_industry(test_session):
    """Create a sample industry for testing."""
    industry = Industry(name="Technology")
    test_session.add(industry)
    test_session.commit()
    test_session.refresh(industry)
    return industry


@pytest.fixture(scope="function")
def sample_company(test_session, sample_industry):
    """Create a sample company for testing."""
    company = Company(
        name="Acme Corp",
        industry_id=sample_industry.id,
        size="100-500",
        website="https://acme.com",
    )
    test_session.add(company)
    test_session.commit()
    test_session.refresh(company)
    return company


# Monkey patch SessionLocal to use test session
@pytest.fixture(autouse=True)
def mock_session_local(monkeypatch, test_session):
    """
    Mock SessionLocal to return test session.

    This ensures CRUD operations use the test transaction,
    which gets rolled back after each test.
    """

    def mock_session_maker():
        return test_session

    monkeypatch.setattr(crud, "SessionLocal", mock_session_maker)


# Tests for create_or_update_company
class TestCreateOrUpdateCompany:
    """Test suite for create_or_update_company function."""

    def test_create_new_company(self, test_session, sample_industry):
        """Test creating a new company."""
        new_company = Company(
            name="Tech Innovations Inc",
            industry_id=sample_industry.id,
            size="50-100",
            website="https://techinnovations.com",
        )

        result = crud.create_or_update_company(new_company)

        assert result is True

        # Verify company was created
        saved_company = (
            test_session.query(Company)
            .filter(Company.name == "Tech Innovations Inc")
            .first()
        )
        assert saved_company is not None
        assert saved_company.name == "Tech Innovations Inc"
        assert saved_company.size == "50-100"
        assert saved_company.website == "https://techinnovations.com"

    def test_create_company_with_minimal_fields(self, test_session, sample_industry):
        """Test creating company with only required fields."""
        minimal_company = Company(
            name="Minimal Corp", industry_id=sample_industry.id, size="10-50"
        )

        result = crud.create_or_update_company(minimal_company)

        assert result is True
        saved = (
            test_session.query(Company).filter(Company.name == "Minimal Corp").first()
        )
        assert saved is not None
        assert saved.name == "Minimal Corp"
        assert saved.website is None

    def test_create_company_with_invalid_industry_fails(self, test_session):
        """Test that creating company with invalid industry_id fails."""
        invalid_company = Company(
            name="Invalid Industry Co",
            industry_id=99999999,  # Non-existent industry
            size="10-50",
        )

        result = crud.create_or_update_company(invalid_company)
        assert result is False


# Tests for get_all_companies
class TestGetAllCompanies:
    """Test suite for get_all_companies function."""

    def test_get_all_companies_empty(self, test_session):
        """Test getting companies when no companies exist in current session."""
        companies = crud.get_all_companies()
        # May have companies from fixtures, so check it's a list
        assert isinstance(companies, list)

    def test_get_all_companies_single(self, test_session, sample_company):
        """Test getting all companies with one company."""
        companies = crud.get_all_companies()

        # Find our sample company
        our_company = next((c for c in companies if c.id == sample_company.id), None)
        assert our_company is not None
        assert our_company.name == sample_company.name
        assert our_company.size == sample_company.size

    def test_get_all_companies_multiple(self, test_session, sample_industry):
        """Test getting all companies with multiple companies."""
        initial_count = len(crud.get_all_companies())

        companies_data = [
            {"name": "Company A", "size": "10-50"},
            {"name": "Company B", "size": "100-500"},
            {"name": "Company C", "size": "500+"},
        ]

        for data in companies_data:
            company = Company(
                name=data["name"], industry_id=sample_industry.id, size=data["size"]
            )
            test_session.add(company)
        test_session.commit()

        all_companies = crud.get_all_companies()

        assert len(all_companies) >= initial_count + 3
        names = [c.name for c in all_companies]
        assert "Company A" in names
        assert "Company B" in names
        assert "Company C" in names


# Tests for get_company_by_id
class TestGetCompanyById:
    """Test suite for get_company_by_id function."""

    def test_get_existing_company(self, test_session, sample_company):
        """Test getting an existing company by ID."""
        company = crud.get_company_by_id(sample_company.id)

        assert company is not None
        assert company.id == sample_company.id
        assert company.name == sample_company.name
        assert company.size == sample_company.size

    def test_get_nonexistent_company(self, test_session):
        """Test getting a company that doesn't exist."""
        company = crud.get_company_by_id(99999999)

        assert company is None

    def test_get_company_with_relationships(
        self, test_session, sample_company, sample_industry
    ):
        """Test that relationships are accessible."""
        # Get IDs before they might become detached
        expected_industry_id = sample_industry.id

        company = crud.get_company_by_id(sample_company.id)

        assert company is not None
        assert company.industry_id == expected_industry_id


# Tests for get_company_by_name
class TestGetCompanyByName:
    """Test suite for get_company_by_name function."""

    def test_get_by_name_single_match(self, test_session, sample_company):
        """Test getting company by exact name match."""
        companies = crud.get_company_by_name("Acme Corp", limit=None)

        # Should find at least our sample company
        acme_corps = [c for c in companies if c.name == "Acme Corp"]
        assert len(acme_corps) >= 1
        assert any(c.id == sample_company.id for c in acme_corps)

    def test_get_by_name_no_match(self, test_session):
        """Test getting company by name with no matches."""
        companies = crud.get_company_by_name("NonexistentCompany12345", limit=None)

        assert companies == []

    def test_get_by_name_with_limit(self, test_session, sample_industry):
        """Test getting companies with limit."""
        # Create multiple companies with same name
        for i in range(5):
            company = Company(
                name="Common Name Corp",
                industry_id=sample_industry.id,
                size="10-50",
                website=f"https://example{i}.com",
            )
            test_session.add(company)
        test_session.commit()

        companies = crud.get_company_by_name("Common Name Corp", limit=2)

        assert len(companies) == 2
        assert all(c.name == "Common Name Corp" for c in companies)

    def test_get_by_name_multiple_matches_no_limit(self, test_session, sample_industry):
        """Test getting all companies with same name."""
        # Create multiple companies
        for i in range(3):
            company = Company(
                name="Same Name Inc",
                industry_id=sample_industry.id,
                size="10-50",
                website=f"https://samename{i}.com",
            )
            test_session.add(company)
        test_session.commit()

        companies = crud.get_company_by_name("Same Name Inc", limit=None)

        assert len(companies) == 3


# Tests for delete_company
class TestDeleteCompany:
    """Test suite for delete_company function."""

    def test_delete_existing_company(self, test_session, sample_company):
        """Test deleting an existing company."""
        company_id = sample_company.id

        result = crud.delete_company(company_id)

        assert result is True

        # Verify company was deleted
        deleted = test_session.query(Company).filter(Company.id == company_id).first()
        assert deleted is None

    def test_delete_nonexistent_company(self, test_session):
        """Test deleting a company that doesn't exist."""
        result = crud.delete_company(99999999)

        assert result is False

    def test_delete_company_twice(self, test_session, sample_company):
        """Test deleting the same company twice."""
        company_id = sample_company.id

        # First deletion
        result1 = crud.delete_company(company_id)
        assert result1 is True

        # Commit to persist the deletion
        test_session.commit()

        # Second deletion should fail
        result2 = crud.delete_company(company_id)
        assert result2 is False


# Integration tests
class TestCompanyCRUDIntegration:
    """Integration tests for Company CRUD operations."""

    def test_create_read_delete_flow(self, test_session, sample_industry):
        """Test complete CRUD flow for Company."""
        # Create
        new_company = Company(
            name="Integration Test Corp",
            industry_id=sample_industry.id,
            size="100-500",
            website="https://integration.com",
        )
        create_result = crud.create_or_update_company(new_company)
        assert create_result is True

        test_session.commit()

        # Get the ID of created company
        created = (
            test_session.query(Company)
            .filter(Company.name == "Integration Test Corp")
            .first()
        )
        assert created is not None
        created_id = created.id

        # Read by ID
        company = crud.get_company_by_id(created_id)
        assert company is not None
        assert company.name == "Integration Test Corp"

        # Delete
        delete_result = crud.delete_company(created_id)
        assert delete_result is True

        test_session.commit()

        # Verify deletion
        deleted = crud.get_company_by_id(created_id)
        assert deleted is None

    def test_multiple_companies_different_industries(self, test_session):
        """Test managing companies from different industries."""
        # Create two industries
        industry1 = Industry(name="Finance")
        industry2 = Industry(name="Healthcare")
        test_session.add(industry1)
        test_session.add(industry2)
        test_session.commit()

        # Get industry IDs before they might become detached
        industry1_id = industry1.id
        industry2_id = industry2.id

        # Create companies for each industry
        company1 = Company(
            name="Finance Corp Unique", industry_id=industry1_id, size="100-500"
        )
        company2 = Company(
            name="Healthcare Inc Unique", industry_id=industry2_id, size="50-100"
        )

        result1 = crud.create_or_update_company(company1)
        result2 = crud.create_or_update_company(company2)

        assert result1 is True
        assert result2 is True

        test_session.commit()

        # Verify both exist
        c1 = (
            test_session.query(Company)
            .filter(Company.name == "Finance Corp Unique")
            .first()
        )
        c2 = (
            test_session.query(Company)
            .filter(Company.name == "Healthcare Inc Unique")
            .first()
        )

        assert c1 is not None
        assert c2 is not None
        assert c1.industry_id == industry1_id
        assert c2.industry_id == industry2_id


# Edge cases and error handling
class TestCompanyEdgeCases:
    """Test edge cases and error handling for Company CRUD."""

    def test_company_without_industry_fails(self, test_session):
        """Test that creating company without valid industry fails."""
        invalid_company = Company(
            name="No Industry Co",
            industry_id=99999999,  # Non-existent industry
            size="10-50",
        )

        result = crud.create_or_update_company(invalid_company)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

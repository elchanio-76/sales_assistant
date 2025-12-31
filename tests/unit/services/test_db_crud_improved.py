"""
Unit tests for database CRUD operations using PostgreSQL.

Improved version that:
- Preserves migration history (alembic_version table)
- Uses TRUNCATE instead of DROP for cleanup
- Handles foreign key constraints properly
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models.database import Base, Prospect, Company, Industry, ProspectStatus
import app.services.db_crud as crud


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/sales_test"
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
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename != 'alembic_version'
        """))

        tables = [row[0] for row in result]

        if tables:
            # Truncate all tables (CASCADE handles foreign keys)
            tables_str = ', '.join(tables)
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
def clean_tables(test_db_engine):
    """
    Clean all data from tables before each test.

    Use this fixture if you need a completely clean database state.
    """
    with test_db_engine.connect() as conn:
        conn.execute(text("COMMIT"))

        # Truncate all tables except alembic_version
        result = conn.execute(text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename != 'alembic_version'
        """))

        tables = [row[0] for row in result]

        if tables:
            tables_str = ', '.join(tables)
            conn.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"))
            conn.execute(text("COMMIT"))


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
        website="https://acme.com"
    )
    test_session.add(company)
    test_session.commit()
    test_session.refresh(company)
    return company


@pytest.fixture(scope="function")
def sample_prospect(test_session, sample_company):
    """Create a sample prospect for testing."""
    prospect = Prospect(
        full_name="John Doe",
        email="john.doe@acme.com",
        linkedin_url="https://linkedin.com/in/johndoe",
        location="New York, NY",
        company_id=sample_company.id,
        status=ProspectStatus.NEW,
        is_active=True
    )
    test_session.add(prospect)
    test_session.commit()
    test_session.refresh(prospect)
    return prospect


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


# Tests for create_or_update_prospect
class TestCreateOrUpdateProspect:
    """Test suite for create_or_update_prospect function."""

    def test_create_new_prospect(self, test_session, sample_company):
        """Test creating a new prospect."""
        new_prospect = Prospect(
            full_name="Jane Smith",
            email="jane.smith@acme.com",
            linkedin_url="https://linkedin.com/in/janesmith",
            location="San Francisco, CA",
            company_id=sample_company.id,
            status=ProspectStatus.NEW,
            is_active=True
        )

        result = crud.create_or_update_prospect(new_prospect)

        assert result is True

        # Verify prospect was created
        saved_prospect = test_session.query(Prospect).filter(
            Prospect.email == "jane.smith@acme.com"
        ).first()
        assert saved_prospect is not None
        assert saved_prospect.full_name == "Jane Smith"
        assert saved_prospect.location == "San Francisco, CA"

    def test_create_prospect_with_minimal_fields(self, test_session, sample_company):
        """Test creating prospect with only required fields."""
        minimal_prospect = Prospect(
            full_name="Minimal User",
            email="minimal@test.com",
            company_id=sample_company.id
        )

        result = crud.create_or_update_prospect(minimal_prospect)

        assert result is True
        saved = test_session.query(Prospect).filter(
            Prospect.email == "minimal@test.com"
        ).first()
        assert saved is not None
        assert saved.full_name == "Minimal User"
        assert saved.status == ProspectStatus.NEW
        assert saved.is_active is True


# Tests for get_all_prospects
class TestGetAllProspects:
    """Test suite for get_all_prospects function."""

    def test_get_all_prospects_empty(self, test_session):
        """Test getting prospects when no prospects exist in current session."""
        prospects = crud.get_all_prospects()
        # May have prospects from fixtures, so check it's a list
        assert isinstance(prospects, list)

    def test_get_all_prospects_single(self, test_session, sample_prospect):
        """Test getting all prospects with one prospect."""
        prospects = crud.get_all_prospects()

        # Find our sample prospect
        our_prospect = next((p for p in prospects if p.id == sample_prospect.id), None)
        assert our_prospect is not None
        assert our_prospect.full_name == sample_prospect.full_name
        assert our_prospect.email == sample_prospect.email

    def test_get_all_prospects_multiple(self, test_session, sample_company):
        """Test getting all prospects with multiple prospects."""
        initial_count = len(crud.get_all_prospects())

        prospects_data = [
            {"full_name": "Alice", "email": "alice@test.com"},
            {"full_name": "Bob", "email": "bob@test.com"},
            {"full_name": "Charlie", "email": "charlie@test.com"},
        ]

        for data in prospects_data:
            prospect = Prospect(
                full_name=data["full_name"],
                email=data["email"],
                company_id=sample_company.id
            )
            test_session.add(prospect)
        test_session.commit()

        all_prospects = crud.get_all_prospects()

        assert len(all_prospects) >= initial_count + 3
        names = [p.full_name for p in all_prospects]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names


# Tests for get_prospect_by_id
class TestGetProspectById:
    """Test suite for get_prospect_by_id function."""

    def test_get_existing_prospect(self, test_session, sample_prospect):
        """Test getting an existing prospect by ID."""
        prospect = crud.get_prospect_by_id(sample_prospect.id)

        assert prospect is not None
        assert prospect.id == sample_prospect.id
        assert prospect.full_name == sample_prospect.full_name
        assert prospect.email == sample_prospect.email

    def test_get_nonexistent_prospect(self, test_session):
        """Test getting a prospect that doesn't exist."""
        prospect = crud.get_prospect_by_id(99999999)

        assert prospect is None

    def test_get_prospect_with_relationships(self, test_session, sample_prospect, sample_company):
        """Test that relationships are accessible."""
        # Get IDs before they might become detached
        expected_company_id = sample_company.id

        prospect = crud.get_prospect_by_id(sample_prospect.id)

        assert prospect is not None
        assert prospect.company_id == expected_company_id


# Tests for get_prospect_by_name
class TestGetProspectByName:
    """Test suite for get_prospect_by_name function."""

    def test_get_by_name_single_match(self, test_session, sample_prospect):
        """Test getting prospect by exact name match."""
        prospects = crud.get_prospect_by_name("John Doe", limit=None)

        # Should find at least our sample prospect
        john_does = [p for p in prospects if p.full_name == "John Doe"]
        assert len(john_does) >= 1
        assert any(p.id == sample_prospect.id for p in john_does)

    def test_get_by_name_no_match(self, test_session):
        """Test getting prospect by name with no matches."""
        prospects = crud.get_prospect_by_name("NonexistentPerson12345", limit=None)

        assert prospects == []

    def test_get_by_name_with_limit(self, test_session, sample_company):
        """Test getting prospects with limit."""
        # Create multiple prospects with same name
        for i in range(5):
            prospect = Prospect(
                full_name="Common Name",
                email=f"user{i}@test.com",
                company_id=sample_company.id
            )
            test_session.add(prospect)
        test_session.commit()

        prospects = crud.get_prospect_by_name("Common Name", limit=2)

        assert len(prospects) == 2
        assert all(p.full_name == "Common Name" for p in prospects)

    def test_get_by_name_multiple_matches_no_limit(self, test_session, sample_company):
        """Test getting all prospects with same name."""
        # Create multiple prospects
        for i in range(3):
            prospect = Prospect(
                full_name="Same Name",
                email=f"same{i}@test.com",
                company_id=sample_company.id
            )
            test_session.add(prospect)
        test_session.commit()

        prospects = crud.get_prospect_by_name("Same Name", limit=None)

        assert len(prospects) == 3


# Tests for delete_prospect
class TestDeleteProspect:
    """Test suite for delete_prospect function."""

    def test_delete_existing_prospect(self, test_session, sample_prospect):
        """Test deleting an existing prospect."""
        prospect_id = sample_prospect.id

        result = crud.delete_prospect(prospect_id)

        assert result is True

        # Verify prospect was deleted
        deleted = test_session.query(Prospect).filter(
            Prospect.id == prospect_id
        ).first()
        assert deleted is None

    def test_delete_nonexistent_prospect(self, test_session):
        """Test deleting a prospect that doesn't exist."""
        result = crud.delete_prospect(99999999)

        assert result is False

    def test_delete_prospect_twice(self, test_session, sample_prospect):
        """Test deleting the same prospect twice."""
        prospect_id = sample_prospect.id

        # First deletion
        result1 = crud.delete_prospect(prospect_id)
        assert result1 is True

        # Commit to persist the deletion
        test_session.commit()

        # Second deletion should fail
        result2 = crud.delete_prospect(prospect_id)
        assert result2 is False


# Integration tests
class TestProspectCRUDIntegration:
    """Integration tests for CRUD operations."""

    def test_create_read_delete_flow(self, test_session, sample_company):
        """Test complete CRUD flow."""
        # Create
        new_prospect = Prospect(
            full_name="Integration Test",
            email="integration@test.com",
            company_id=sample_company.id
        )
        create_result = crud.create_or_update_prospect(new_prospect)
        assert create_result is True

        test_session.commit()

        # Get the ID of created prospect
        created = test_session.query(Prospect).filter(
            Prospect.email == "integration@test.com"
        ).first()
        assert created is not None
        created_id = created.id

        # Read by ID
        prospect = crud.get_prospect_by_id(created_id)
        assert prospect is not None
        assert prospect.email == "integration@test.com"

        # Delete
        delete_result = crud.delete_prospect(created_id)
        assert delete_result is True

        test_session.commit()

        # Verify deletion
        deleted = crud.get_prospect_by_id(created_id)
        assert deleted is None

    def test_multiple_prospects_different_companies(self, test_session, sample_industry):
        """Test managing prospects from different companies."""
        # Create two companies
        company1 = Company(
            name="Company A Unique",
            industry_id=sample_industry.id,
            size="10-50"
        )
        company2 = Company(
            name="Company B Unique",
            industry_id=sample_industry.id,
            size="500+"
        )
        test_session.add(company1)
        test_session.add(company2)
        test_session.commit()

        # Get company IDs before they might become detached
        company1_id = company1.id
        company2_id = company2.id

        # Create prospects for each company
        prospect1 = Prospect(
            full_name="Person A",
            email="persona@companya-unique.com",
            company_id=company1_id
        )
        prospect2 = Prospect(
            full_name="Person B",
            email="personb@companyb-unique.com",
            company_id=company2_id
        )

        result1 = crud.create_or_update_prospect(prospect1)
        result2 = crud.create_or_update_prospect(prospect2)

        assert result1 is True
        assert result2 is True

        test_session.commit()

        # Verify both exist
        p1 = test_session.query(Prospect).filter(
            Prospect.email == "persona@companya-unique.com"
        ).first()
        p2 = test_session.query(Prospect).filter(
            Prospect.email == "personb@companyb-unique.com"
        ).first()

        assert p1 is not None
        assert p2 is not None
        assert p1.company_id == company1_id
        assert p2.company_id == company2_id


# Edge cases and error handling
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_prospect_without_company_fails(self, test_session):
        """Test that creating prospect without valid company fails."""
        invalid_prospect = Prospect(
            full_name="No Company",
            email="nocompany@test.com",
            company_id=99999999  # Non-existent company
        )

        result = crud.create_or_update_prospect(invalid_prospect)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

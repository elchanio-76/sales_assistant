"""
Unit tests for ProspectResearch CRUD operations using PostgreSQL.

Following the same pattern as other CRUD test files.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models.database import Base, ProspectResearch, Prospect, Company, Industry, ProspectStatus
import app.services.db_crud as crud


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/sales_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a PostgreSQL test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    yield engine

    # Minimal cleanup
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename != 'alembic_version'
        """))
        tables = [row[0] for row in result]
        if tables:
            tables_str = ', '.join(tables)
            conn.execute(text(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE"))
            conn.execute(text("COMMIT"))
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_db_engine):
    """Create a test database session with transaction rollback."""
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
        name="Test Corp",
        industry_id=sample_industry.id,
        size="100-500"
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
        email="john@example.com",
        company_id=sample_company.id,
        status=ProspectStatus.NEW
    )
    test_session.add(prospect)
    test_session.commit()
    test_session.refresh(prospect)
    return prospect


@pytest.fixture(scope="function")
def sample_research(test_session, sample_prospect):
    """Create a sample prospect research for testing."""
    research = ProspectResearch(
        prospect_id=sample_prospect.id,
        research_summary="Test research summary",
        key_insights=["insight1", "insight2"],
        recommended_solutions=[{"solution": "AWS EC2"}],
        confidence_score=0.85
    )
    test_session.add(research)
    test_session.commit()
    test_session.refresh(research)
    return research


@pytest.fixture(autouse=True)
def mock_session_local(monkeypatch, test_session):
    """Mock SessionLocal to return test session."""
    def mock_session_maker():
        return test_session
    monkeypatch.setattr(crud, "SessionLocal", mock_session_maker)


# Tests for create_or_update_prospect_research
class TestCreateOrUpdateProspectResearch:
    """Test suite for create_or_update_prospect_research function."""

    def test_create_new_research(self, test_session, sample_prospect):
        """Test creating new prospect research."""
        new_research = ProspectResearch(
            prospect_id=sample_prospect.id,
            research_summary="New research findings",
            key_insights=["finding1", "finding2"],
            confidence_score=0.9
        )

        result = crud.create_or_update_prospect_research(new_research)
        assert result is True

        # Verify created
        saved = test_session.query(ProspectResearch).filter(
            ProspectResearch.research_summary == "New research findings"
        ).first()
        assert saved is not None
        assert saved.confidence_score == 0.9

    def test_create_research_with_minimal_fields(self, test_session, sample_prospect):
        """Test creating research with only required fields."""
        minimal_research = ProspectResearch(
            prospect_id=sample_prospect.id,
            research_summary="Minimal research"
        )

        result = crud.create_or_update_prospect_research(minimal_research)
        assert result is True

    def test_create_research_with_invalid_prospect_fails(self, test_session):
        """Test that creating research with invalid prospect_id fails."""
        invalid_research = ProspectResearch(
            prospect_id=99999999,
            research_summary="Invalid research"
        )

        result = crud.create_or_update_prospect_research(invalid_research)
        assert result is False


# Tests for get_all_prospect_research
class TestGetAllProspectResearch:
    """Test suite for get_all_prospect_research function."""

    def test_get_all_research(self, test_session, sample_research):
        """Test getting all prospect research."""
        research_list = crud.get_all_prospect_research()

        assert isinstance(research_list, list)
        our_research = next((r for r in research_list if r.id == sample_research.id), None)
        assert our_research is not None


# Tests for get_prospect_research_by_id
class TestGetProspectResearchById:
    """Test suite for get_prospect_research_by_id function."""

    def test_get_existing_research(self, test_session, sample_research):
        """Test getting existing research by ID."""
        research = crud.get_prospect_research_by_id(sample_research.id)

        assert research is not None
        assert research.id == sample_research.id
        assert research.research_summary == sample_research.research_summary

    def test_get_nonexistent_research(self, test_session):
        """Test getting non-existent research."""
        research = crud.get_prospect_research_by_id(99999999)
        assert research is None


# Tests for get_prospect_research_by_prospect_id
class TestGetProspectResearchByProspectId:
    """Test suite for get_prospect_research_by_prospect_id function."""

    def test_get_research_by_prospect_id(self, test_session, sample_prospect, sample_research):
        """Test getting research by prospect ID."""
        prospect_id = sample_prospect.id
        research_list = crud.get_prospect_research_by_prospect_id(prospect_id)

        assert len(research_list) >= 1
        assert any(r.id == sample_research.id for r in research_list)

    def test_get_research_for_nonexistent_prospect(self, test_session):
        """Test getting research for non-existent prospect."""
        research_list = crud.get_prospect_research_by_prospect_id(99999999)
        assert research_list == []

    def test_multiple_research_for_same_prospect(self, test_session, sample_prospect):
        """Test multiple research records for same prospect."""
        prospect_id = sample_prospect.id

        # Create multiple research records
        for i in range(3):
            research = ProspectResearch(
                prospect_id=prospect_id,
                research_summary=f"Research {i}"
            )
            test_session.add(research)
        test_session.commit()

        research_list = crud.get_prospect_research_by_prospect_id(prospect_id)
        assert len(research_list) >= 3


# Tests for delete_prospect_research
class TestDeleteProspectResearch:
    """Test suite for delete_prospect_research function."""

    def test_delete_existing_research(self, test_session, sample_research):
        """Test deleting existing research."""
        research_id = sample_research.id

        result = crud.delete_prospect_research(research_id)
        assert result is True

        # Verify deleted
        deleted = test_session.query(ProspectResearch).filter(
            ProspectResearch.id == research_id
        ).first()
        assert deleted is None

    def test_delete_nonexistent_research(self, test_session):
        """Test deleting non-existent research."""
        result = crud.delete_prospect_research(99999999)
        assert result is False


# Integration tests
class TestProspectResearchIntegration:
    """Integration tests for ProspectResearch CRUD operations."""

    def test_create_read_delete_flow(self, test_session, sample_prospect):
        """Test complete CRUD flow."""
        # Create
        new_research = ProspectResearch(
            prospect_id=sample_prospect.id,
            research_summary="Integration test research"
        )
        create_result = crud.create_or_update_prospect_research(new_research)
        assert create_result is True

        test_session.commit()

        # Read
        created = test_session.query(ProspectResearch).filter(
            ProspectResearch.research_summary == "Integration test research"
        ).first()
        assert created is not None
        created_id = created.id

        # Delete
        delete_result = crud.delete_prospect_research(created_id)
        assert delete_result is True

        test_session.commit()

        # Verify deletion
        deleted = crud.get_prospect_research_by_id(created_id)
        assert deleted is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

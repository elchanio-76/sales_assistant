"""
Unit tests for remaining CRUD operations: Interaction, OutreachDraft, Event, and LLMUsageLog.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os

# Add app directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from app.models.database import (
    Base,
    Interaction,
    OutreachDraft,
    Event,
    LLMUsageLog,
    Prospect,
    Company,
    Industry,
    ProspectStatus,
    InteractionType,
)
import app.services.db_crud as crud


# Test database configuration
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sales_test"
)


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a PostgreSQL test database engine."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    yield engine

    # Minimal cleanup
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        result = conn.execute(
            text(
                """
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public' AND tablename != 'alembic_version'
        """
            )
        )
        tables = [row[0] for row in result]
        if tables:
            tables_str = ", ".join(tables)
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
    company = Company(name="Test Corp", industry_id=sample_industry.id, size="100-500")
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
        status=ProspectStatus.NEW,
    )
    test_session.add(prospect)
    test_session.commit()
    test_session.refresh(prospect)
    return prospect


@pytest.fixture(scope="function")
def sample_event(test_session):
    """Create a sample event for testing."""
    event = Event(
        event_type="conference",
        event_date=datetime(2025, 6, 15),
        description="AWS Summit 2025",
        location="Las Vegas, NV",
        status="planned",
    )
    test_session.add(event)
    test_session.commit()
    test_session.refresh(event)
    return event


@pytest.fixture(autouse=True)
def mock_session_local(monkeypatch, test_session):
    """Mock SessionLocal to return test session."""

    def mock_session_maker():
        return test_session

    monkeypatch.setattr(crud, "SessionLocal", mock_session_maker)


# ============================================================================
# Interaction Tests
# ============================================================================


class TestInteractionCRUD:
    """Test suite for Interaction CRUD operations."""

    def test_create_interaction(self, test_session, sample_prospect):
        """Test creating a new interaction."""
        interaction = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            interaction_date=datetime.now(),
            subject="Initial outreach",
            content="Test email content",
        )

        result = crud.create_or_update_interaction(interaction)
        assert result is True

    def test_create_interaction_with_invalid_prospect_fails(self, test_session):
        """Test that creating interaction with invalid prospect_id fails."""
        interaction = Interaction(
            prospect_id=99999999,
            interaction_type=InteractionType.EMAIL,
            interaction_date=datetime.now(),
            subject="Test",
            content="Test content",
        )

        result = crud.create_or_update_interaction(interaction)
        assert result is False

    def test_get_all_interactions(self, test_session, sample_prospect):
        """Test getting all interactions."""
        # Create test interaction
        interaction = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.CALL,
            interaction_date=datetime.now(),
            subject="Follow-up call",
            content="Discussed requirements",
        )
        test_session.add(interaction)
        test_session.commit()

        interactions = crud.get_all_interactions()
        assert isinstance(interactions, list)
        assert len(interactions) >= 1

    def test_get_interaction_by_id(self, test_session, sample_prospect):
        """Test getting interaction by ID."""
        interaction = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.MEETING,
            interaction_date=datetime.now(),
            subject="Product demo",
            content="Demonstrated key features",
        )
        test_session.add(interaction)
        test_session.commit()
        test_session.refresh(interaction)

        retrieved = crud.get_interaction_by_id(interaction.id)
        assert retrieved is not None
        assert retrieved.subject == "Product demo"

    def test_get_interactions_by_prospect_id(self, test_session, sample_prospect):
        """Test getting interactions by prospect ID."""
        # Create multiple interactions
        for i in range(3):
            interaction = Interaction(
                prospect_id=sample_prospect.id,
                interaction_type=InteractionType.EMAIL,
                interaction_date=datetime.now(),
                subject=f"Email {i}",
                content=f"Content {i}",
            )
            test_session.add(interaction)
        test_session.commit()

        interactions = crud.get_interactions_by_prospect_id(sample_prospect.id)
        assert len(interactions) >= 3

    def test_get_interactions_by_type(self, test_session, sample_prospect):
        """Test getting interactions by type."""
        interaction = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EVENT,
            interaction_date=datetime.now(),
            subject="Trade show",
            content="Met at booth",
        )
        test_session.add(interaction)
        test_session.commit()

        interactions = crud.get_interactions_by_type(InteractionType.EVENT)
        assert len(interactions) >= 1
        assert all(i.interaction_type == InteractionType.EVENT for i in interactions)

    def test_delete_interaction(self, test_session, sample_prospect):
        """Test deleting an interaction."""
        interaction = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            interaction_date=datetime.now(),
            subject="Test",
            content="Test content",
        )
        test_session.add(interaction)
        test_session.commit()
        interaction_id = interaction.id

        result = crud.delete_interaction(interaction_id)
        assert result is True

        deleted = (
            test_session.query(Interaction)
            .filter(Interaction.id == interaction_id)
            .first()
        )
        assert deleted is None


# ============================================================================
# OutreachDraft Tests
# ============================================================================


class TestOutreachDraftCRUD:
    """Test suite for OutreachDraft CRUD operations."""

    def test_create_outreach_draft(self, test_session, sample_prospect):
        """Test creating a new outreach draft."""
        draft = OutreachDraft(
            prospect_id=sample_prospect.id,
            draft_type="email",
            content="Draft email content",
            status="draft",
        )

        result = crud.create_or_update_outreach_draft(draft)
        assert result is True

    def test_create_draft_with_invalid_prospect_fails(self, test_session):
        """Test that creating draft with invalid prospect_id fails."""
        draft = OutreachDraft(
            prospect_id=99999999,
            draft_type="email",
            content="Test content",
            status="draft",
        )

        result = crud.create_or_update_outreach_draft(draft)
        assert result is False

    def test_get_all_outreach_drafts(self, test_session, sample_prospect):
        """Test getting all outreach drafts."""
        draft = OutreachDraft(
            prospect_id=sample_prospect.id,
            draft_type="linkedin",
            content="LinkedIn message",
            status="draft",
        )
        test_session.add(draft)
        test_session.commit()

        drafts = crud.get_all_outreach_drafts()
        assert isinstance(drafts, list)
        assert len(drafts) >= 1

    def test_get_outreach_draft_by_id(self, test_session, sample_prospect):
        """Test getting outreach draft by ID."""
        draft = OutreachDraft(
            prospect_id=sample_prospect.id,
            draft_type="email",
            content="Test content",
            status="draft",
        )
        test_session.add(draft)
        test_session.commit()
        test_session.refresh(draft)

        retrieved = crud.get_outreach_draft_by_id(draft.id)
        assert retrieved is not None
        assert retrieved.draft_type == "email"

    def test_get_drafts_by_prospect_id(self, test_session, sample_prospect):
        """Test getting drafts by prospect ID."""
        for i in range(2):
            draft = OutreachDraft(
                prospect_id=sample_prospect.id,
                draft_type="email",
                content=f"Content {i}",
                status="draft",
            )
            test_session.add(draft)
        test_session.commit()

        drafts = crud.get_outreach_drafts_by_prospect_id(sample_prospect.id)
        assert len(drafts) >= 2

    def test_get_drafts_by_status(self, test_session, sample_prospect):
        """Test getting drafts by status."""
        draft = OutreachDraft(
            prospect_id=sample_prospect.id,
            draft_type="email",
            content="Sent content",
            status="sent",
        )
        test_session.add(draft)
        test_session.commit()

        drafts = crud.get_outreach_drafts_by_status("sent")
        assert len(drafts) >= 1
        assert all(d.status == "sent" for d in drafts)

    def test_delete_outreach_draft(self, test_session, sample_prospect):
        """Test deleting an outreach draft."""
        draft = OutreachDraft(
            prospect_id=sample_prospect.id,
            draft_type="email",
            content="Test",
            status="draft",
        )
        test_session.add(draft)
        test_session.commit()
        draft_id = draft.id

        result = crud.delete_outreach_draft(draft_id)
        assert result is True

        deleted = (
            test_session.query(OutreachDraft)
            .filter(OutreachDraft.id == draft_id)
            .first()
        )
        assert deleted is None


# ============================================================================
# Event Tests
# ============================================================================


class TestEventCRUD:
    """Test suite for Event CRUD operations."""

    def test_create_event(self, test_session):
        """Test creating a new event."""
        event = Event(
            event_type="webinar",
            event_date=datetime(2025, 7, 1),
            description="AWS Webinar",
            location="Online",
            status="scheduled",
        )

        result = crud.create_or_update_event(event)
        assert result is True

    def test_get_all_events(self, test_session, sample_event):
        """Test getting all events."""
        events = crud.get_all_events()
        assert isinstance(events, list)
        assert len(events) >= 1

    def test_get_event_by_id(self, test_session, sample_event):
        """Test getting event by ID."""
        event = crud.get_event_by_id(sample_event.id)
        assert event is not None
        assert event.event_type == "conference"

    def test_get_events_by_type(self, test_session):
        """Test getting events by type."""
        event = Event(
            event_type="workshop",
            event_date=datetime(2025, 8, 1),
            description="Hands-on workshop",
            location="Seattle, WA",
            status="scheduled",
        )
        test_session.add(event)
        test_session.commit()

        events = crud.get_events_by_type("workshop")
        assert len(events) >= 1
        assert all(e.event_type == "workshop" for e in events)

    def test_delete_event(self, test_session, sample_event):
        """Test deleting an event."""
        event_id = sample_event.id

        result = crud.delete_event(event_id)
        assert result is True

        deleted = test_session.query(Event).filter(Event.id == event_id).first()
        assert deleted is None


# ============================================================================
# LLMUsageLog Tests
# ============================================================================


class TestLLMUsageLog:
    """Test suite for LLMUsageLog logging functions."""

    def test_log_llm_usage(self, test_session):
        """Test logging LLM usage."""
        result = crud.log_llm_usage(
            workflow_name="prospect_research",
            node_name="analyze_company",
            model="gpt-4",
            prompt_tokens=500,
            completion_tokens=200,
            total_tokens=700,
            latency_ms=1200,
            cost=0.05,
        )

        assert result is True

        # Verify log was created
        logs = test_session.query(LLMUsageLog).all()
        assert len(logs) >= 1

    def test_log_llm_usage_with_minimal_params(self, test_session):
        """Test logging with only required parameters."""
        result = crud.log_llm_usage(
            workflow_name="outreach_generation",
            node_name="draft_email",
            model="gpt-3.5-turbo",
        )

        assert result is True

    def test_get_llm_usage_logs(self, test_session):
        """Test getting LLM usage logs."""
        # Create test logs
        crud.log_llm_usage("test_workflow", "node1", "gpt-4")
        crud.log_llm_usage("test_workflow", "node2", "gpt-4")

        logs = crud.get_llm_usage_logs(workflow_name="test_workflow")
        assert len(logs) >= 2

    def test_get_llm_usage_logs_by_model(self, test_session):
        """Test getting logs filtered by model."""
        crud.log_llm_usage("workflow1", "node1", "claude-3")
        crud.log_llm_usage("workflow2", "node2", "gpt-4")

        logs = crud.get_llm_usage_logs(model="claude-3")
        assert len(logs) >= 1
        assert all(log.model == "claude-3" for log in logs)

    def test_get_llm_usage_logs_with_limit(self, test_session):
        """Test getting logs with limit."""
        for i in range(5):
            crud.log_llm_usage(f"workflow_{i}", "node", "gpt-4")

        logs = crud.get_llm_usage_logs(limit=2)
        assert len(logs) == 2

    def test_get_llm_usage_stats(self, test_session):
        """Test getting aggregated usage statistics."""
        # Create test logs with known values
        crud.log_llm_usage(
            "test_workflow",
            "node1",
            "gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.01,
            latency_ms=1000,
        )
        crud.log_llm_usage(
            "test_workflow",
            "node2",
            "gpt-4",
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            cost=0.02,
            latency_ms=1500,
        )

        stats = crud.get_llm_usage_stats(workflow_name="test_workflow")

        assert stats["total_calls"] == 2
        assert stats["total_prompt_tokens"] == 300
        assert stats["total_completion_tokens"] == 150
        assert stats["total_tokens"] == 450
        assert stats["total_cost"] == 0.03
        assert stats["avg_latency_ms"] == 1250.0

    def test_get_llm_usage_stats_empty(self, test_session):
        """Test getting stats when no logs exist."""
        stats = crud.get_llm_usage_stats(workflow_name="nonexistent_workflow")

        assert stats["total_calls"] == 0
        assert stats["total_cost"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

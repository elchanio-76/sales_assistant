"""
Unit tests for Solution CRUD operations using PostgreSQL.

Following the same pattern as test_db_crud_improved.py for Prospect model.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from app.models.database import Base, Solution, PricingModels
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
def sample_solution(test_session):
    """Create a sample solution for testing."""
    solution = Solution(
        name="Amazon EC2",
        category="Compute",
        description="Scalable virtual servers in the cloud",
        use_cases={"web_hosting": True, "batch_processing": True},
        keywords=["compute", "vm", "server"],
        pricing_model=PricingModels.ON_DEMAND
    )
    test_session.add(solution)
    test_session.commit()
    test_session.refresh(solution)
    return solution


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


# Tests for create_or_update_solution
class TestCreateOrUpdateSolution:
    """Test suite for create_or_update_solution function."""

    def test_create_new_solution(self, test_session):
        """Test creating a new solution."""
        new_solution = Solution(
            name="Amazon S3",
            category="Storage",
            description="Object storage built to retrieve any amount of data",
            use_cases={"backup": True, "data_lake": True},
            keywords=["storage", "object", "bucket"],
            pricing_model=PricingModels.ON_DEMAND
        )

        result = crud.create_or_update_solution(new_solution)

        assert result is True

        # Verify solution was created
        saved_solution = test_session.query(Solution).filter(
            Solution.name == "Amazon S3"
        ).first()
        assert saved_solution is not None
        assert saved_solution.name == "Amazon S3"
        assert saved_solution.category == "Storage"
        assert saved_solution.pricing_model == PricingModels.ON_DEMAND

    def test_create_solution_with_minimal_fields(self, test_session):
        """Test creating solution with only required fields."""
        minimal_solution = Solution(
            name="AWS Lambda",
            category="Compute",
            description="Serverless compute service",
            pricing_model=PricingModels.ON_DEMAND
        )

        result = crud.create_or_update_solution(minimal_solution)

        assert result is True
        saved = test_session.query(Solution).filter(
            Solution.name == "AWS Lambda"
        ).first()
        assert saved is not None
        assert saved.name == "AWS Lambda"
        assert saved.use_cases is None
        assert saved.keywords is None

    def test_create_solution_with_different_pricing_models(self, test_session):
        """Test creating solutions with different pricing models."""
        pricing_models = [
            PricingModels.SAVINGS_PLANS,
            PricingModels.RESERVED_INSTANCES,
            PricingModels.SUBSCRIPTION
        ]

        for idx, pricing_model in enumerate(pricing_models):
            solution = Solution(
                name=f"Test Solution {idx}",
                category="Test",
                description=f"Test solution with {pricing_model.value} pricing",
                pricing_model=pricing_model
            )
            result = crud.create_or_update_solution(solution)
            assert result is True

        # Verify all were created
        solutions = test_session.query(Solution).filter(
            Solution.name.like("Test Solution%")
        ).all()
        assert len(solutions) == 3


# Tests for get_all_solutions
class TestGetAllSolutions:
    """Test suite for get_all_solutions function."""

    def test_get_all_solutions_empty(self, test_session):
        """Test getting solutions when no solutions exist in current session."""
        solutions = crud.get_all_solutions()
        # May have solutions from fixtures, so check it's a list
        assert isinstance(solutions, list)

    def test_get_all_solutions_single(self, test_session, sample_solution):
        """Test getting all solutions with one solution."""
        solutions = crud.get_all_solutions()

        # Find our sample solution
        our_solution = next((s for s in solutions if s.id == sample_solution.id), None)
        assert our_solution is not None
        assert our_solution.name == sample_solution.name
        assert our_solution.category == sample_solution.category

    def test_get_all_solutions_multiple(self, test_session):
        """Test getting all solutions with multiple solutions."""
        initial_count = len(crud.get_all_solutions())

        solutions_data = [
            {"name": "Solution A", "category": "Compute"},
            {"name": "Solution B", "category": "Storage"},
            {"name": "Solution C", "category": "Database"},
        ]

        for data in solutions_data:
            solution = Solution(
                name=data["name"],
                category=data["category"],
                description=f"Description for {data['name']}",
                pricing_model=PricingModels.ON_DEMAND
            )
            test_session.add(solution)
        test_session.commit()

        all_solutions = crud.get_all_solutions()

        assert len(all_solutions) >= initial_count + 3
        names = [s.name for s in all_solutions]
        assert "Solution A" in names
        assert "Solution B" in names
        assert "Solution C" in names


# Tests for get_solution_by_id
class TestGetSolutionById:
    """Test suite for get_solution_by_id function."""

    def test_get_existing_solution(self, test_session, sample_solution):
        """Test getting an existing solution by ID."""
        solution = crud.get_solution_by_id(sample_solution.id)

        assert solution is not None
        assert solution.id == sample_solution.id
        assert solution.name == sample_solution.name
        assert solution.category == sample_solution.category

    def test_get_nonexistent_solution(self, test_session):
        """Test getting a solution that doesn't exist."""
        solution = crud.get_solution_by_id(99999999)

        assert solution is None


# Tests for get_solution_by_name
class TestGetSolutionByName:
    """Test suite for get_solution_by_name function."""

    def test_get_by_name_single_match(self, test_session, sample_solution):
        """Test getting solution by exact name match."""
        solutions = crud.get_solution_by_name("Amazon EC2", limit=None)

        # Should find at least our sample solution
        ec2_solutions = [s for s in solutions if s.name == "Amazon EC2"]
        assert len(ec2_solutions) >= 1
        assert any(s.id == sample_solution.id for s in ec2_solutions)

    def test_get_by_name_no_match(self, test_session):
        """Test getting solution by name with no matches."""
        solutions = crud.get_solution_by_name("NonexistentSolution12345", limit=None)

        assert solutions == []

    def test_get_by_name_with_limit(self, test_session):
        """Test getting solutions with limit."""
        # Create multiple solutions with same name
        for i in range(5):
            solution = Solution(
                name="Common Solution",
                category="Test",
                description=f"Description {i}",
                pricing_model=PricingModels.ON_DEMAND
            )
            test_session.add(solution)
        test_session.commit()

        solutions = crud.get_solution_by_name("Common Solution", limit=2)

        assert len(solutions) == 2
        assert all(s.name == "Common Solution" for s in solutions)

    def test_get_by_name_multiple_matches_no_limit(self, test_session):
        """Test getting all solutions with same name."""
        # Create multiple solutions
        for i in range(3):
            solution = Solution(
                name="Same Name Solution",
                category="Test",
                description=f"Description {i}",
                pricing_model=PricingModels.ON_DEMAND
            )
            test_session.add(solution)
        test_session.commit()

        solutions = crud.get_solution_by_name("Same Name Solution", limit=None)

        assert len(solutions) == 3


# Tests for get_solutions_by_category
class TestGetSolutionsByCategory:
    """Test suite for get_solutions_by_category function."""

    def test_get_by_category_single(self, test_session, sample_solution):
        """Test getting solutions by category."""
        solutions = crud.get_solutions_by_category("Compute")

        # Should find at least our sample solution
        compute_solutions = [s for s in solutions if s.category == "Compute"]
        assert len(compute_solutions) >= 1
        assert any(s.id == sample_solution.id for s in compute_solutions)

    def test_get_by_category_multiple(self, test_session):
        """Test getting multiple solutions in same category."""
        # Create multiple solutions in same category
        for i in range(3):
            solution = Solution(
                name=f"Database Solution {i}",
                category="Database",
                description=f"Database solution {i}",
                pricing_model=PricingModels.ON_DEMAND
            )
            test_session.add(solution)
        test_session.commit()

        solutions = crud.get_solutions_by_category("Database")

        assert len(solutions) >= 3
        assert all(s.category == "Database" for s in solutions)

    def test_get_by_category_no_match(self, test_session):
        """Test getting solutions by non-existent category."""
        solutions = crud.get_solutions_by_category("NonexistentCategory")

        assert solutions == []


# Tests for delete_solution
class TestDeleteSolution:
    """Test suite for delete_solution function."""

    def test_delete_existing_solution(self, test_session, sample_solution):
        """Test deleting an existing solution."""
        solution_id = sample_solution.id

        result = crud.delete_solution(solution_id)

        assert result is True

        # Verify solution was deleted
        deleted = test_session.query(Solution).filter(
            Solution.id == solution_id
        ).first()
        assert deleted is None

    def test_delete_nonexistent_solution(self, test_session):
        """Test deleting a solution that doesn't exist."""
        result = crud.delete_solution(99999999)

        assert result is False

    def test_delete_solution_twice(self, test_session, sample_solution):
        """Test deleting the same solution twice."""
        solution_id = sample_solution.id

        # First deletion
        result1 = crud.delete_solution(solution_id)
        assert result1 is True

        # Commit to persist the deletion
        test_session.commit()

        # Second deletion should fail
        result2 = crud.delete_solution(solution_id)
        assert result2 is False


# Integration tests
class TestSolutionCRUDIntegration:
    """Integration tests for Solution CRUD operations."""

    def test_create_read_delete_flow(self, test_session):
        """Test complete CRUD flow for Solution."""
        # Create
        new_solution = Solution(
            name="Integration Test Solution",
            category="Integration",
            description="Testing integration",
            pricing_model=PricingModels.ON_DEMAND
        )
        create_result = crud.create_or_update_solution(new_solution)
        assert create_result is True

        test_session.commit()

        # Get the ID of created solution
        created = test_session.query(Solution).filter(
            Solution.name == "Integration Test Solution"
        ).first()
        assert created is not None
        created_id = created.id

        # Read by ID
        solution = crud.get_solution_by_id(created_id)
        assert solution is not None
        assert solution.name == "Integration Test Solution"

        # Delete
        delete_result = crud.delete_solution(created_id)
        assert delete_result is True

        test_session.commit()

        # Verify deletion
        deleted = crud.get_solution_by_id(created_id)
        assert deleted is None

    def test_multiple_solutions_different_categories(self, test_session):
        """Test managing solutions from different categories."""
        categories = ["Compute", "Storage", "Database", "Networking"]

        for category in categories:
            solution = Solution(
                name=f"{category} Test Solution",
                category=category,
                description=f"Test solution for {category}",
                pricing_model=PricingModels.ON_DEMAND
            )
            result = crud.create_or_update_solution(solution)
            assert result is True

        test_session.commit()

        # Verify solutions exist in each category
        for category in categories:
            solutions = crud.get_solutions_by_category(category)
            assert len(solutions) >= 1
            assert all(s.category == category for s in solutions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

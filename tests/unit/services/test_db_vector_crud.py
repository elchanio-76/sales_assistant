"""
Unit tests for Vector CRUD operations using PostgreSQL.

Following the same pattern as test_db_crud_solution.py.
Tests both InteractionVector and SolutionVector CRUD operations.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys
import os
import numpy as np

# Add app directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)

from app.models.database import (
    Base,
    InteractionVector,
    SolutionVector,
    Interaction,
    Solution,
    Prospect,
    Company,
    Industry,
    InteractionType,
    PricingModels,
    ProspectStatus,
)
from app.config.settings import VectorTables
import app.services.db_vector_crud as vector_crud


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
        name="Example Corp",
        industry_id=sample_industry.id,
        size="500-1000",
        website="https://example.com",
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
        email="john.doe@example.com",
        company_id=sample_company.id,
        status=ProspectStatus.NEW,
    )
    test_session.add(prospect)
    test_session.commit()
    test_session.refresh(prospect)
    return prospect


@pytest.fixture(scope="function")
def sample_interaction(test_session, sample_prospect):
    """Create a sample interaction for testing."""
    interaction = Interaction(
        prospect_id=sample_prospect.id,
        interaction_type=InteractionType.EMAIL,
        interaction_date=datetime.now(),
        subject="Test Email",
        content="This is a test email content for vector embedding.",
    )
    test_session.add(interaction)
    test_session.commit()
    test_session.refresh(interaction)
    return interaction


@pytest.fixture(scope="function")
def sample_solution(test_session):
    """Create a sample solution for testing."""
    solution = Solution(
        name="Amazon EC2",
        category="Compute",
        description="Scalable virtual servers in the cloud",
        use_cases={"web_hosting": True, "batch_processing": True},
        keywords=["compute", "vm", "server"],
        pricing_model=PricingModels.ON_DEMAND,
    )
    test_session.add(solution)
    test_session.commit()
    test_session.refresh(solution)
    return solution


@pytest.fixture(scope="function")
def sample_embedding():
    """Create a sample 384-dimensional embedding vector."""
    # Create a random 384-dimensional vector (matching all-MiniLM-L6-v2 dimensions)
    return np.random.rand(384).tolist()


@pytest.fixture(scope="function")
def sample_interaction_vector(test_session, sample_interaction, sample_embedding):
    """Create a sample interaction vector for testing."""
    interaction_vector = InteractionVector(
        interaction_id=sample_interaction.id, embedding=sample_embedding
    )
    test_session.add(interaction_vector)
    test_session.commit()
    test_session.refresh(interaction_vector)
    return interaction_vector


@pytest.fixture(scope="function")
def sample_solution_vector(test_session, sample_solution, sample_embedding):
    """Create a sample solution vector for testing."""
    solution_vector = SolutionVector(
        solution_id=sample_solution.id, embedding=sample_embedding
    )
    test_session.add(solution_vector)
    test_session.commit()
    test_session.refresh(solution_vector)
    return solution_vector


# Monkey patch get_db_session to use test session
@pytest.fixture(autouse=True)
def mock_session_local(monkeypatch, test_session):
    """
    Mock get_db_session to return test session.

    This ensures CRUD operations use the test transaction,
    which gets rolled back after each test.
    """
    from contextlib import contextmanager

    @contextmanager
    def mock_get_db_session():
        yield test_session

    monkeypatch.setattr(vector_crud, "get_db_session", mock_get_db_session)


# ============================================================================
# Tests for InteractionVector CRUD Operations
# ============================================================================


class TestCreateInteractionVector:
    """Test suite for create_interaction_vector function."""

    def test_create_new_interaction_vector(
        self, test_session, sample_interaction, sample_embedding
    ):
        """Test creating a new interaction vector."""
        result = vector_crud.create_interaction_vector(
            sample_interaction.id, sample_embedding
        )

        assert result is not None
        assert result.interaction_id == sample_interaction.id
        assert result.embedding is not None
        assert len(result.embedding) == 384

    def test_create_interaction_vector_with_different_dimensions(
        self, test_session, sample_interaction
    ):
        """Test creating interaction vector with correct dimensions."""
        embedding = np.random.rand(384).tolist()

        result = vector_crud.create_interaction_vector(sample_interaction.id, embedding)

        assert result is not None
        assert len(result.embedding) == 384


class TestGetInteractionVectorById:
    """Test suite for get_interaction_vector_by_id function."""

    def test_get_existing_interaction_vector(
        self, test_session, sample_interaction_vector
    ):
        """Test getting an existing interaction vector by ID."""
        vector = vector_crud.get_interaction_vector_by_id(
            sample_interaction_vector.id
        )

        assert vector is not None
        assert vector.id == sample_interaction_vector.id
        assert vector.interaction_id == sample_interaction_vector.interaction_id

    def test_get_nonexistent_interaction_vector(self, test_session):
        """Test getting an interaction vector that doesn't exist."""
        vector = vector_crud.get_interaction_vector_by_id(99999999)

        assert vector is None


class TestDeleteInteractionVector:
    """Test suite for delete_interaction_vector function."""

    def test_delete_existing_interaction_vector(
        self, test_session, sample_interaction_vector
    ):
        """Test deleting an existing interaction vector."""
        vector_id = sample_interaction_vector.id

        result = vector_crud.delete_interaction_vector(vector_id)

        assert result is True

        # Verify vector was deleted
        deleted = (
            test_session.query(InteractionVector)
            .filter(InteractionVector.id == vector_id)
            .first()
        )
        assert deleted is None

    def test_delete_nonexistent_interaction_vector(self, test_session):
        """Test deleting an interaction vector that doesn't exist."""
        result = vector_crud.delete_interaction_vector(99999999)

        assert result is False

    def test_delete_interaction_vector_twice(
        self, test_session, sample_interaction_vector
    ):
        """Test deleting the same interaction vector twice."""
        vector_id = sample_interaction_vector.id

        # First deletion
        result1 = vector_crud.delete_interaction_vector(vector_id)
        assert result1 is True

        test_session.commit()

        # Second deletion should fail
        result2 = vector_crud.delete_interaction_vector(vector_id)
        assert result2 is False


class TestUpdateInteractionVector:
    """Test suite for update_interaction_vector function."""

    def test_update_existing_interaction_vector(
        self, test_session, sample_interaction_vector
    ):
        """Test updating an existing interaction vector."""
        # Store old embedding values before update
        old_embedding = list(sample_interaction_vector.embedding[:5])
        new_embedding = np.random.rand(384).tolist()

        result = vector_crud.update_interaction_vector(
            sample_interaction_vector.id, new_embedding
        )

        assert result is not None
        assert result.id == sample_interaction_vector.id
        # Verify embedding was updated
        result_emb = list(result.embedding[:5])
        assert result_emb == new_embedding[:5]
        assert result_emb != old_embedding

    def test_update_nonexistent_interaction_vector(self, test_session):
        """Test updating an interaction vector that doesn't exist."""
        new_embedding = np.random.rand(384).tolist()

        result = vector_crud.update_interaction_vector(99999999, new_embedding)

        assert result is None


# ============================================================================
# Tests for SolutionVector CRUD Operations
# ============================================================================


class TestCreateSolutionVector:
    """Test suite for create_solution_vector function."""

    def test_create_new_solution_vector(
        self, test_session, sample_solution, sample_embedding
    ):
        """Test creating a new solution vector."""
        result = vector_crud.create_solution_vector(sample_solution.id, sample_embedding)

        assert result is not None
        assert result.solution_id == sample_solution.id
        assert result.embedding is not None
        assert len(result.embedding) == 384

    def test_create_solution_vector_with_different_dimensions(
        self, test_session, sample_solution
    ):
        """Test creating solution vector with correct dimensions."""
        embedding = np.random.rand(384).tolist()

        result = vector_crud.create_solution_vector(sample_solution.id, embedding)

        assert result is not None
        assert len(result.embedding) == 384


class TestGetSolutionVectorById:
    """Test suite for get_solution_vector_by_id function."""

    def test_get_existing_solution_vector(self, test_session, sample_solution_vector):
        """Test getting an existing solution vector by ID."""
        vector = vector_crud.get_solution_vector_by_id(sample_solution_vector.id)

        assert vector is not None
        assert vector.id == sample_solution_vector.id
        assert vector.solution_id == sample_solution_vector.solution_id

    def test_get_nonexistent_solution_vector(self, test_session):
        """Test getting a solution vector that doesn't exist."""
        vector = vector_crud.get_solution_vector_by_id(99999999)

        assert vector is None


class TestDeleteSolutionVector:
    """Test suite for delete_solution_vector function."""

    def test_delete_existing_solution_vector(
        self, test_session, sample_solution_vector
    ):
        """Test deleting an existing solution vector."""
        vector_id = sample_solution_vector.id

        result = vector_crud.delete_solution_vector(vector_id)

        assert result is True

        # Verify vector was deleted
        deleted = (
            test_session.query(SolutionVector)
            .filter(SolutionVector.id == vector_id)
            .first()
        )
        assert deleted is None

    def test_delete_nonexistent_solution_vector(self, test_session):
        """Test deleting a solution vector that doesn't exist."""
        result = vector_crud.delete_solution_vector(99999999)

        assert result is False

    def test_delete_solution_vector_twice(self, test_session, sample_solution_vector):
        """Test deleting the same solution vector twice."""
        vector_id = sample_solution_vector.id

        # First deletion
        result1 = vector_crud.delete_solution_vector(vector_id)
        assert result1 is True

        test_session.commit()

        # Second deletion should fail
        result2 = vector_crud.delete_solution_vector(vector_id)
        assert result2 is False


class TestUpdateSolutionVector:
    """Test suite for update_solution_vector function."""

    def test_update_existing_solution_vector(
        self, test_session, sample_solution_vector
    ):
        """Test updating an existing solution vector."""
        # Store old embedding values before update
        old_embedding = list(sample_solution_vector.embedding[:5])
        new_embedding = np.random.rand(384).tolist()

        result = vector_crud.update_solution_vector(
            sample_solution_vector.id, new_embedding
        )

        assert result is not None
        assert result.id == sample_solution_vector.id
        # Verify embedding was updated
        result_emb = list(result.embedding[:5])
        assert result_emb == new_embedding[:5]
        assert result_emb != old_embedding

    def test_update_nonexistent_solution_vector(self, test_session):
        """Test updating a solution vector that doesn't exist."""
        new_embedding = np.random.rand(384).tolist()

        result = vector_crud.update_solution_vector(99999999, new_embedding)

        assert result is None


# ============================================================================
# Integration Tests
# ============================================================================


class TestVectorCRUDIntegration:
    """Integration tests for Vector CRUD operations."""

    def test_interaction_vector_complete_flow(
        self, test_session, sample_interaction, sample_embedding
    ):
        """Test complete CRUD flow for InteractionVector."""
        # Create
        created = vector_crud.create_interaction_vector(
            sample_interaction.id, sample_embedding
        )
        assert created is not None
        created_id = created.id

        # Read
        retrieved = vector_crud.get_interaction_vector_by_id(created_id)
        assert retrieved is not None
        assert retrieved.interaction_id == sample_interaction.id

        # Update
        new_embedding = np.random.rand(384).tolist()
        updated = vector_crud.update_interaction_vector(created_id, new_embedding)
        assert updated is not None
        # Verify embedding changed (convert to list for comparison)
        assert list(updated.embedding[:5]) != sample_embedding[:5]

        # Delete
        deleted = vector_crud.delete_interaction_vector(created_id)
        assert deleted is True

        # Verify deletion
        verify = vector_crud.get_interaction_vector_by_id(created_id)
        assert verify is None

    def test_solution_vector_complete_flow(
        self, test_session, sample_solution, sample_embedding
    ):
        """Test complete CRUD flow for SolutionVector."""
        # Create
        created = vector_crud.create_solution_vector(
            sample_solution.id, sample_embedding
        )
        assert created is not None
        created_id = created.id

        # Read
        retrieved = vector_crud.get_solution_vector_by_id(created_id)
        assert retrieved is not None
        assert retrieved.solution_id == sample_solution.id

        # Update
        new_embedding = np.random.rand(384).tolist()
        updated = vector_crud.update_solution_vector(created_id, new_embedding)
        assert updated is not None
        # Verify embedding changed (convert to list for comparison)
        assert list(updated.embedding[:5]) != sample_embedding[:5]

        # Delete
        deleted = vector_crud.delete_solution_vector(created_id)
        assert deleted is True

        # Verify deletion
        verify = vector_crud.get_solution_vector_by_id(created_id)
        assert verify is None

    def test_multiple_vectors_for_same_interaction(
        self, test_session, sample_interaction
    ):
        """Test creating multiple vectors for the same interaction."""
        embeddings = [np.random.rand(384).tolist() for _ in range(3)]

        created_vectors = []
        for embedding in embeddings:
            vector = vector_crud.create_interaction_vector(
                sample_interaction.id, embedding
            )
            assert vector is not None
            created_vectors.append(vector)

        # Verify all vectors exist
        for vector in created_vectors:
            retrieved = vector_crud.get_interaction_vector_by_id(vector.id)
            assert retrieved is not None
            assert retrieved.interaction_id == sample_interaction.id

    def test_multiple_vectors_for_same_solution(self, test_session, sample_solution):
        """Test creating multiple vectors for the same solution."""
        embeddings = [np.random.rand(384).tolist() for _ in range(3)]

        created_vectors = []
        for embedding in embeddings:
            vector = vector_crud.create_solution_vector(sample_solution.id, embedding)
            assert vector is not None
            created_vectors.append(vector)

        # Verify all vectors exist
        for vector in created_vectors:
            retrieved = vector_crud.get_solution_vector_by_id(vector.id)
            assert retrieved is not None
            assert retrieved.solution_id == sample_solution.id


# ============================================================================
# Tests for Vector Search Operations
# ============================================================================


class TestVectorSearchText:
    """Test suite for vector_search_text function."""

    @pytest.fixture
    def mock_get_embedding(self, monkeypatch, sample_embedding):
        """Mock the get_embedding function to return a known embedding."""

        def mock_embedding(text):
            return sample_embedding

        monkeypatch.setattr("app.services.db_vector_crud.get_embedding", mock_embedding)
        return mock_embedding

    @pytest.fixture
    def multiple_solution_vectors(self, test_session, sample_solution):
        """Create multiple solution vectors for search testing."""
        vectors = []
        for i in range(5):
            embedding = np.random.rand(384).tolist()
            solution_vector = SolutionVector(
                solution_id=sample_solution.id, embedding=embedding
            )
            test_session.add(solution_vector)
            vectors.append(solution_vector)

        test_session.commit()
        for vec in vectors:
            test_session.refresh(vec)
        return vectors

    @pytest.fixture
    def multiple_interaction_vectors(self, test_session, sample_interaction):
        """Create multiple interaction vectors for search testing."""
        vectors = []
        for i in range(5):
            embedding = np.random.rand(384).tolist()
            interaction_vector = InteractionVector(
                interaction_id=sample_interaction.id, embedding=embedding
            )
            test_session.add(interaction_vector)
            vectors.append(interaction_vector)

        test_session.commit()
        for vec in vectors:
            test_session.refresh(vec)
        return vectors

    def test_search_solutions_table(
        self, test_session, multiple_solution_vectors, mock_get_embedding
    ):
        """Test searching in the solutions table."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        assert len(results) <= 5

    def test_search_interactions_table(
        self, test_session, multiple_interaction_vectors, mock_get_embedding
    ):
        """Test searching in the interactions table."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.INTERACTIONS, limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        assert len(results) <= 5

    def test_search_with_limit(
        self, test_session, multiple_solution_vectors, mock_get_embedding
    ):
        """Test that the limit parameter works correctly."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=3, threshold=1.0
        )

        assert len(results) <= 3

    def test_search_with_threshold(
        self, test_session, multiple_solution_vectors, mock_get_embedding
    ):
        """Test that the threshold parameter filters results."""
        # With a very low threshold (0.0), we should get fewer or no results
        results_low = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=0.0
        )

        # With a very high threshold (1.0), we should get more results
        results_high = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
        )

        # Results with higher threshold should be >= results with lower threshold
        assert len(results_high) >= len(results_low)

    def test_search_returns_correct_structure_solutions(
        self, test_session, sample_solution_vector, mock_get_embedding
    ):
        """Test that search results have the correct structure for solutions."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
        )

        if results:
            for result in results:
                assert "id" in result
                assert "solution_id" in result
                assert "distance" in result
                assert isinstance(result["id"], int)
                assert isinstance(result["solution_id"], int)

    def test_search_returns_correct_structure_interactions(
        self, test_session, sample_interaction_vector, mock_get_embedding
    ):
        """Test that search results have the correct structure for interactions."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.INTERACTIONS, limit=5, threshold=1.0
        )

        if results:
            for result in results:
                assert "id" in result
                assert "interaction_id" in result
                assert "distance" in result
                assert isinstance(result["id"], int)
                assert isinstance(result["interaction_id"], int)

    def test_search_with_invalid_table(self, test_session, mock_get_embedding):
        """Test searching with an invalid table name."""
        # This should raise ValueError according to the implementation
        with pytest.raises(ValueError, match="Invalid table name"):
            vector_crud.vector_search_text(
                query="test query", table="INVALID_TABLE", limit=5, threshold=0.5
            )

    def test_search_empty_table(self, test_session, mock_get_embedding):
        """Test searching in an empty table."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_orders_by_distance(
        self, test_session, multiple_solution_vectors, mock_get_embedding
    ):
        """Test that search results are ordered by cosine distance."""
        results = vector_crud.vector_search_text(
            query="test query", table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
        )

        if len(results) > 1:
            distances = [result["distance"] for result in results]
            # Distances should be in ascending order (most similar first)
            assert distances == sorted(distances)

    def test_search_with_different_queries(
        self, test_session, multiple_solution_vectors, mock_get_embedding
    ):
        """Test searching with different query strings."""
        queries = ["compute services", "database solutions", "storage options"]

        for query in queries:
            results = vector_crud.vector_search_text(
                query=query, table=VectorTables.SOLUTIONS, limit=5, threshold=1.0
            )
            assert isinstance(results, list)


# ============================================================================
# Tests for Filtered Vector Search Operations
# ============================================================================


class TestSearchSolutionWithFilters:
    """Test suite for search_solution_with_filters function."""

    @pytest.fixture
    def mock_get_embedding(self, monkeypatch, sample_embedding):
        """Mock the get_embedding function to return a known embedding."""

        def mock_embedding(text):
            return sample_embedding

        monkeypatch.setattr("app.services.db_vector_crud.get_embedding", mock_embedding)
        return mock_embedding

    @pytest.fixture
    def solutions_with_different_attributes(self, test_session):
        """Create multiple solutions with different categories and keywords."""
        solutions = []

        # Compute solutions
        tech_solution1 = Solution(
            name="Cloud Computing Platform",
            category="Compute",
            description="Scalable cloud infrastructure",
            use_cases={"web_hosting": True},
            keywords=["cloud", "compute", "scalable"],
            pricing_model=PricingModels.ON_DEMAND,
        )
        tech_solution2 = Solution(
            name="Container Service",
            category="Compute",
            description="Container orchestration platform",
            use_cases={"microservices": True},
            keywords=["container", "docker", "kubernetes"],
            pricing_model=PricingModels.ON_DEMAND,
        )

        # Database solutions
        db_solution = Solution(
            name="Managed Database",
            category="Database",
            description="Fully managed database service",
            use_cases={"data_storage": True},
            keywords=["database", "managed", "sql"],
            pricing_model=PricingModels.ON_DEMAND,
        )

        for sol in [tech_solution1, tech_solution2, db_solution]:
            test_session.add(sol)

        test_session.commit()
        for sol in [tech_solution1, tech_solution2, db_solution]:
            test_session.refresh(sol)
            solutions.append(sol)

        return solutions

    @pytest.fixture
    def solution_vectors_with_filters(
        self, test_session, solutions_with_different_attributes
    ):
        """Create solution vectors for the solutions with different attributes."""
        vectors = []
        for solution in solutions_with_different_attributes:
            embedding = np.random.rand(384).tolist()
            solution_vector = SolutionVector(
                solution_id=solution.id, embedding=embedding
            )
            test_session.add(solution_vector)
            vectors.append(solution_vector)

        test_session.commit()
        for vec in vectors:
            test_session.refresh(vec)
        return vectors

    def test_search_with_no_filters(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test searching without any filters."""
        results = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=[], limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        assert len(results) <= 5

    def test_search_with_category_filter(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test searching with category filter."""
        results = vector_crud.search_solution_with_filters(
            query="test query", category="Compute", keywords=[], limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        # Should find solutions in Compute category

    def test_search_with_keyword_filter(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test searching with keyword filter."""
        results = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=["cloud"], limit=5, threshold=1.0
        )

        assert isinstance(results, list)
        # Should find solutions with 'cloud' in keywords

    def test_search_with_multiple_keywords(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test searching with multiple keywords."""
        results = vector_crud.search_solution_with_filters(
            query="test query",
            category="",
            keywords=["cloud", "compute"],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)

    def test_search_returns_correct_structure(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test that results have the correct structure."""
        results = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=[], limit=5, threshold=1.0
        )

        if results:
            for result in results:
                assert "id" in result
                assert "solution_id" in result
                assert "distance" in result
                assert isinstance(result["id"], int)
                assert isinstance(result["solution_id"], int)
                assert isinstance(result["distance"], float)

    def test_search_with_limit(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test that limit parameter works correctly."""
        results = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=[], limit=2, threshold=1.0
        )

        assert len(results) <= 2

    def test_search_with_threshold(
        self, test_session, solution_vectors_with_filters, mock_get_embedding
    ):
        """Test that threshold parameter filters results."""
        results_low = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=[], limit=5, threshold=0.0
        )

        results_high = vector_crud.search_solution_with_filters(
            query="test query", category="", keywords=[], limit=5, threshold=1.0
        )

        assert len(results_high) >= len(results_low)

    def test_search_empty_results(self, test_session, mock_get_embedding):
        """Test searching with no matching results."""
        results = vector_crud.search_solution_with_filters(
            query="test query",
            category="NonExistentCategory",
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)


class TestSearchInteractionVectorWithFilters:
    """Test suite for search_interaction_vector_with_filters function."""

    @pytest.fixture
    def mock_get_embedding(self, monkeypatch, sample_embedding):
        """Mock the get_embedding function to return a known embedding."""

        def mock_embedding(text):
            return sample_embedding

        monkeypatch.setattr("app.services.db_vector_crud.get_embedding", mock_embedding)
        return mock_embedding

    @pytest.fixture
    def interactions_with_different_types(self, test_session, sample_prospect):
        """Create multiple interactions with different types and content."""
        interactions = []

        # Email interactions
        email1 = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            interaction_date=datetime.now(),
            subject="Product Demo",
            content="Interested in cloud computing solutions",
        )
        email2 = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            interaction_date=datetime.now(),
            subject="Follow Up",
            content="Following up on database requirements",
        )

        # Call interaction
        call = Interaction(
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.CALL,
            interaction_date=datetime.now(),
            subject="Initial Call",
            content="Discussion about infrastructure needs",
        )

        for interaction in [email1, email2, call]:
            test_session.add(interaction)

        test_session.commit()
        for interaction in [email1, email2, call]:
            test_session.refresh(interaction)
            interactions.append(interaction)

        return interactions

    @pytest.fixture
    def interaction_vectors_with_filters(
        self, test_session, interactions_with_different_types
    ):
        """Create interaction vectors for interactions with different types."""
        vectors = []
        for interaction in interactions_with_different_types:
            embedding = np.random.rand(384).tolist()
            interaction_vector = InteractionVector(
                interaction_id=interaction.id, embedding=embedding
            )
            test_session.add(interaction_vector)
            vectors.append(interaction_vector)

        test_session.commit()
        for vec in vectors:
            test_session.refresh(vec)
        return vectors

    def test_search_by_prospect_id(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test searching interactions by prospect_id."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)
        assert len(results) <= 5

    def test_search_with_interaction_type_filter(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test searching with interaction type filter."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)
        # Should only return email interactions

    def test_search_with_keyword_filter(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test searching with keyword filter."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=["cloud"],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)

    def test_search_with_all_filters(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test searching with all filters combined."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=InteractionType.EMAIL,
            keywords=["cloud"],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)

    def test_search_returns_correct_structure(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test that results have the correct structure."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        if results:
            for result in results:
                assert "id" in result
                assert "interaction_id" in result
                assert "distance" in result
                assert isinstance(result["id"], int)
                assert isinstance(result["interaction_id"], int)
                assert isinstance(result["distance"], float)

    def test_search_with_limit(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test that limit parameter works correctly."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=[],
            limit=2,
            threshold=1.0,
        )

        assert len(results) <= 2

    def test_search_with_threshold(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test that threshold parameter filters results."""
        results_low = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=[],
            limit=5,
            threshold=0.0,
        )

        results_high = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=sample_prospect.id,
            interaction_type=None,
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        assert len(results_high) >= len(results_low)

    def test_search_nonexistent_prospect(
        self, test_session, interaction_vectors_with_filters, mock_get_embedding
    ):
        """Test searching for interactions of a non-existent prospect."""
        results = vector_crud.search_interaction_vector_with_filters(
            query="test query",
            prospect_id=99999999,
            interaction_type=None,
            keywords=[],
            limit=5,
            threshold=1.0,
        )

        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_with_different_interaction_types(
        self,
        test_session,
        sample_prospect,
        interaction_vectors_with_filters,
        mock_get_embedding,
    ):
        """Test searching with different interaction types."""
        for interaction_type in [InteractionType.EMAIL, InteractionType.CALL]:
            results = vector_crud.search_interaction_vector_with_filters(
                query="test query",
                prospect_id=sample_prospect.id,
                interaction_type=interaction_type,
                keywords=[],
                limit=5,
                threshold=1.0,
            )
            assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

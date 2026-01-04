from app.models import database as db
from enum import Enum
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, Session
from pgvector.sqlalchemy import Vector
import logging
from contextlib import contextmanager
from app.services.vector_service import get_embedding, chunk_and_embed_text
from app.config.settings import Settings, VectorTables
import os
from dotenv import load_dotenv

import numpy as np
from numpy.linalg import norm


def cosine_distance(a, b):
    """Calculate cosine distance between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return 1 - np.dot(a, b) / (norm(a) * norm(b))


logger = logging.getLogger(__name__)


settings = Settings()
engine = create_engine(settings.DB_URL, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ============================================================================
# Interaction Vector CRUD Operations
# ============================================================================


def create_interaction_vector(
    interaction_id: int, embedding: Vector
) -> db.InteractionVector | None:
    """Create a new interaction vector in the database."""
    with get_db_session() as session:
        interaction_vector = db.InteractionVector(
            interaction_id=interaction_id, embedding=embedding
        )
        try:
            session.add(interaction_vector)
            session.commit()
            session.refresh(interaction_vector)
            return interaction_vector
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating interaction vector: {e}")
            return None


def get_interaction_vector_by_id(
    interaction_vector_id: int,
) -> db.InteractionVector | None:
    """Get an interaction vector by its ID."""
    with get_db_session() as session:
        try:
            interaction_vector = (
                session.query(db.InteractionVector)
                .filter(db.InteractionVector.id == interaction_vector_id)
                .first()
            )
            return interaction_vector
        except exc.SQLAlchemyError as e:
            logger.error(f"Error getting interaction vector: {e}")
            return None


def delete_interaction_vector(interaction_vector_id: int) -> bool:
    """Delete an interaction vector by its ID."""
    with get_db_session() as session:
        try:
            interaction_vector = (
                session.query(db.InteractionVector)
                .filter(db.InteractionVector.id == interaction_vector_id)
                .first()
            )
            if interaction_vector:
                session.delete(interaction_vector)
                session.commit()
                return True
            return False
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting interaction vector: {e}")
            return False


def update_interaction_vector(
    interaction_vector_id: int, new_embedding: Vector
) -> db.InteractionVector | None:
    """Update an interaction vector's embedding by its ID."""
    with get_db_session() as session:
        try:
            interaction_vector = (
                session.query(db.InteractionVector)
                .filter(db.InteractionVector.id == interaction_vector_id)
                .first()
            )
            if interaction_vector:
                interaction_vector.embedding = new_embedding
                session.commit()
                session.refresh(interaction_vector)
                return interaction_vector
            return None
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating interaction vector: {e}")
            return None


# ============================================================================
# Solution Vector CRUD Operations
# ============================================================================


def create_solution_vector(
    solution_id: int, embedding: Vector
) -> db.SolutionVector | None:
    """Create a new solution vector in the database."""
    with get_db_session() as session:
        solution_vector = db.SolutionVector(
            solution_id=solution_id, embedding=embedding
        )
        try:
            session.add(solution_vector)
            session.commit()
            session.refresh(solution_vector)
            return solution_vector
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error creating solution vector: {e}")
            return None


def get_solution_vector_by_id(solution_vector_id: int) -> db.SolutionVector | None:
    """Get a solution vector by its ID."""
    with get_db_session() as session:
        try:
            solution_vector = (
                session.query(db.SolutionVector)
                .filter(db.SolutionVector.id == solution_vector_id)
                .first()
            )
            return solution_vector
        except exc.SQLAlchemyError as e:
            logger.error(f"Error getting solution vector: {e}")
            return None


def delete_solution_vector(solution_vector_id: int) -> bool:
    """Delete a solution vector by its ID."""
    with get_db_session() as session:
        try:
            solution_vector = (
                session.query(db.SolutionVector)
                .filter(db.SolutionVector.id == solution_vector_id)
                .first()
            )
            if solution_vector:
                session.delete(solution_vector)
                session.commit()
                return True
            return False
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting solution vector: {e}")
            return False


def update_solution_vector(
    solution_vector_id: int, new_embedding: Vector
) -> db.SolutionVector | None:
    """Update a solution vector's embedding by its ID."""
    with get_db_session() as session:
        try:
            solution_vector = (
                session.query(db.SolutionVector)
                .filter(db.SolutionVector.id == solution_vector_id)
                .first()
            )
            if solution_vector:
                solution_vector.embedding = new_embedding
                session.commit()
                session.refresh(solution_vector)
                return solution_vector
            return None
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error updating solution vector: {e}")
            return None


# ============================================================================
# Vector Search Operations
# ============================================================================

def vector_search_text(
    query: str, table: VectorTables, limit: int = 5, threshold: float = 0.5
) -> list[dict]:
    """Search for similar vectors in the database."""

    with get_db_session() as session:
        try:
            if table == VectorTables.SOLUTIONS:
                query_embedding = get_embedding(query)
                results = (
                    session.query(db.SolutionVector)
                    .order_by(
                        db.SolutionVector.embedding.cosine_distance(query_embedding)
                    )
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": result.id,
                        "solution_id": result.solution_id,
                        "distance": cosine_distance(result.embedding, query_embedding),
                    }
                    for result in results
                    if cosine_distance(result.embedding, query_embedding) < threshold
                ]
            elif table == VectorTables.INTERACTIONS:
                query_embedding = get_embedding(query)
                results = (
                    session.query(db.InteractionVector)
                    .order_by(
                        db.InteractionVector.embedding.cosine_distance(query_embedding)
                    )
                    .limit(limit)
                    .all()
                )
                return [
                    {
                        "id": result.id,
                        "interaction_id": result.interaction_id,
                        "distance": cosine_distance(result.embedding, query_embedding),
                    }
                    for result in results
                    if cosine_distance(result.embedding, query_embedding) < threshold
                ]
            else:
                raise ValueError("Invalid table name")
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error searching for similar vectors: {e}")
            return []


def search_solution_with_filters(
    query: str,
    category: str,
    keywords: list[str],
    limit: int = 5,
    threshold: float = 0.5,
) -> list[dict]:
    """Search for similar solutions in the database with filters."""
    with get_db_session() as session:
        try:
            query_embedding = get_embedding(query)
            results = (
                session.query(db.SolutionVector)
                .join(db.Solution, db.SolutionVector.solution_id == db.Solution.id)
                .filter(db.Solution.category == category if category else True)
                .filter(db.Solution.keywords.contains(keywords) if keywords else True)
                .order_by(db.SolutionVector.embedding.cosine_distance(query_embedding))
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": result.id,
                    "solution_id": result.solution_id,
                    "distance": cosine_distance(result.embedding, query_embedding),
                }
                for result in results
                if cosine_distance(result.embedding, query_embedding) < threshold
            ]
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error searching for similar solutions: {e}")
            return []


def search_interaction_vector_with_filters(
    query: str,
    prospect_id: int,
    interaction_type: Enum | None,
    keywords: list[str],
    limit: int = 5,
    threshold: float = 0.5,
) -> list[dict]:
    """Search for similar interactions in the database with filters."""
    with get_db_session() as session:
        try:
            from sqlalchemy import or_

            query_embedding = get_embedding(query)

            # Build query with filters
            query_builder = (
                session.query(db.InteractionVector)
                .join(
                    db.Interaction,
                    db.InteractionVector.interaction_id == db.Interaction.id,
                )
                .filter(db.Interaction.prospect_id == prospect_id)
            )

            # Add interaction type filter if provided
            if interaction_type:
                query_builder = query_builder.filter(
                    db.Interaction.interaction_type == interaction_type
                )

            # Add keyword filters - search for any keyword in content (case-insensitive)
            if keywords:
                keyword_filters = [
                    db.Interaction.content.ilike(f"%{keyword}%")
                    for keyword in keywords
                ]
                query_builder = query_builder.filter(or_(*keyword_filters))

            # Execute query with ordering and limit
            results = (
                query_builder
                .order_by(
                    db.InteractionVector.embedding.cosine_distance(query_embedding)
                )
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": result.id,
                    "interaction_id": result.interaction_id,
                    "distance": cosine_distance(result.embedding, query_embedding),
                }
                for result in results
                if cosine_distance(result.embedding, query_embedding) < threshold
            ]
        except exc.SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error searching for similar interactions: {e}")
            return []

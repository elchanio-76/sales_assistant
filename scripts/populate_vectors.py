from pathlib import Path
import sys
import logging
from datetime import datetime


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
print(f"Project root: {project_root}")

from app.models.database import (
    Solution,
    Interaction,
    SolutionVector,
    InteractionVector,
)
from app.services.db_crud import get_db_session, get_all_solutions, get_all_interactions

from app.services.vector_service import chunk_and_embed_text

from sqlalchemy import text

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def populate_vectors_table(table_name: str):
    """
    Populates the vectors table with data from the specified table.

    Args:
        table_name (str): The name of the table to populate the vectors table with.
    """
    with get_db_session() as session:
        try:
            if table_name == "solutions":
                solutions = get_all_solutions()
                for solution in solutions:
                    embeddings = chunk_and_embed_text(
                        f"{solution.name}\n{solution.description}"
                    )
                    for embedding in embeddings:
                        solution_vector = SolutionVector(
                            solution_id=solution.id,
                            embedding=embedding,
                        )
                        session.add(solution_vector)
            elif table_name == "interactions":
                interactions = get_all_interactions()
                for interaction in interactions:
                    embeddings = chunk_and_embed_text(
                        f"{interaction.subject}\n{interaction.content}"
                    )
                    for embedding in embeddings:
                        interaction_vector = InteractionVector(
                            interaction_id=interaction.id,
                            embedding=interaction.embedding,
                        )
                    session.add(interaction_vector)
            else:
                logger.error(f"Invalid table name: {table_name}")
                return

            session.commit()
            logger.info(
                f"Successfully populated {table_name}_vectors table with {len(solutions)} records."
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Error populating {table_name}_vectors table: {e}")


def clear_vectors_table(table_name: str):
    """
    Clears the vectors table for the specified table.

    Args:
        table_name (str): The name of the table to clear
    """
    with get_db_session() as session:
        try:
            if table_name == "solutions":
                session.query(SolutionVector).delete()
            elif table_name == "interactions":
                session.query(InteractionVector).delete()
            else:
                logger.error(f"Invalid table name: {table_name}")
                return

            session.commit()
            logger.info(f"Successfully cleared {table_name}_vectors table.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error clearing {table_name}_vectors table: {e}")


def main():
    """
    Main function to populate the vectors table.
    """
    if len(sys.argv) != 2:
        logger.error("Usage: python populate_vectors.py <table_name>")
        sys.exit(1)

    table_name = sys.argv[1]
    if table_name not in ["solutions", "interactions"]:
        logger.error("Invalid table name. Use 'solutions' or 'interactions'.")
        sys.exit(1)

    logger.info(f"Starting to populate {table_name}_vectors table...")
    start_time = datetime.now()

    clear_vectors_table(table_name)
    populate_vectors_table(table_name)

    end_time = datetime.now()
    logger.info(
        f"Finished populating {table_name}_vectors table in {end_time - start_time}."
    )


if __name__ == "__main__":
    main()

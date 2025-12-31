from app.models import database as db

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, Session
import logging
from contextlib import contextmanager

import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from app.config.settings import Settings

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
# Prospect CRUD Operations
# ============================================================================

def create_or_update_prospect(prospect: db.Prospect) -> bool:
    """
    Create or update a prospect in the database.

    Args:
        prospect: Prospect object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(prospect)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # Check if it's a foreign key violation
            # Foreign key violations cannot be fixed with merge
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key constraint' in error_msg.lower() or 'fkey' in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {e}")
                return False

            # For other integrity errors (like unique constraints), try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(prospect)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging prospect: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating prospect: {e}")
            session.rollback()
            result = False

    return result

def get_all_prospects() -> list[db.Prospect]:
    """
    Retrieve all prospects from the database.

    Returns:
        List of Prospect objects
    """
    prospects = []
    with get_db_session() as session:
        try:
            prospects = session.query(db.Prospect).all()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospects: {e}")

    return prospects

def get_prospect_by_id(prospect_id: int) -> db.Prospect | None:
    """
    Retrieve a prospect by its ID.

    Args:
        prospect_id: ID of the prospect to retrieve

    Returns:
        Prospect object if found, None otherwise
    """
    prospect = None

    with get_db_session() as session:
        try:
            prospect = session.query(db.Prospect).filter(db.Prospect.id == prospect_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospect: {e}")

    return prospect

def get_prospect_by_name(name: str, limit: int | None = None) -> list[db.Prospect]:
    """
    Retrieve prospects by name.

    Args:
        name: Name of the prospect to search for
        limit: Optional limit on number of results

    Returns:
        List of matching Prospect objects
    """
    prospects = []

    with get_db_session() as session:
        try:
            if limit is not None:
                prospects = session.query(db.Prospect).filter(db.Prospect.full_name == name).limit(limit).all()
            else:
                prospects = session.query(db.Prospect).filter(db.Prospect.full_name == name).all()
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospect: {e}")

    return prospects

def delete_prospect(prospect_id: int) -> bool:
    """
    Delete a prospect by its ID.

    Args:
        prospect_id: ID of the prospect to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            prospect = session.query(db.Prospect).filter(db.Prospect.id == prospect_id).first()
            if prospect:
                logger.info(f"Deleting prospect with id {prospect_id}")
                session.delete(prospect)
                session.commit()
                result = True
            else:
                logger.warning(f"Prospect with id {prospect_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting prospect: {e}")
            session.rollback()

    return result


# ============================================================================
# Company CRUD Operations
# ============================================================================

def create_or_update_company(company: db.Company) -> bool:
    """
    Create or update a company in the database.

    Args:
        company: Company object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(company)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # Check if it's a foreign key violation
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key constraint' in error_msg.lower() or 'fkey' in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {e}")
                return False

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(company)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging company: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating company: {e}")
            session.rollback()
            result = False

    return result


def get_all_companies() -> list[db.Company]:
    """
    Retrieve all companies from the database.

    Returns:
        List of Company objects
    """
    with get_db_session() as session:
        try:
            companies = session.query(db.Company).all()
            return companies
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching companies: {e}")
            return []


def get_company_by_id(company_id: int) -> db.Company | None:
    """
    Retrieve a company by its ID.

    Args:
        company_id: ID of the company to retrieve

    Returns:
        Company object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            company = session.query(db.Company).filter(
                db.Company.id == company_id
            ).first()
            return company
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching company: {e}")
            return None


def get_company_by_name(name: str, limit: int | None = None) -> list[db.Company]:
    """
    Retrieve companies by name.

    Args:
        name: Name of the company to search for
        limit: Optional limit on number of results

    Returns:
        List of matching Company objects
    """
    with get_db_session() as session:
        try:
            query = session.query(db.Company).filter(db.Company.name == name)
            if limit is not None:
                query = query.limit(limit)
            companies = query.all()
            return companies
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching company: {e}")
            return []


def delete_company(company_id: int) -> bool:
    """
    Delete a company by its ID.

    Args:
        company_id: ID of the company to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            company = session.query(db.Company).filter(db.Company.id == company_id).first()
            if company:
                logger.info(f"Deleting company with id {company_id}")
                session.delete(company)
                session.commit()
                result = True
            else:
                logger.warning(f"Company with id {company_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting company: {e}")
            session.rollback()

    return result


# ============================================================================
# Solution (AWSolution) CRUD Operations
# ============================================================================

def create_or_update_solution(solution: db.Solution) -> bool:
    """
    Create or update a solution in the database.

    Args:
        solution: Solution object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(solution)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(solution)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging solution: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating solution: {e}")
            session.rollback()
            result = False

    return result


def get_all_solutions() -> list[db.Solution]:
    """
    Retrieve all solutions from the database.

    Returns:
        List of Solution objects
    """
    with get_db_session() as session:
        try:
            solutions = session.query(db.Solution).all()
            return solutions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching solutions: {e}")
            return []


def get_solution_by_id(solution_id: int) -> db.Solution | None:
    """
    Retrieve a solution by its ID.

    Args:
        solution_id: ID of the solution to retrieve

    Returns:
        Solution object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            solution = session.query(db.Solution).filter(
                db.Solution.id == solution_id
            ).first()
            return solution
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching solution: {e}")
            return None


def get_solution_by_name(name: str, limit: int | None = None) -> list[db.Solution]:
    """
    Retrieve solutions by name.

    Args:
        name: Name of the solution to search for
        limit: Optional limit on number of results

    Returns:
        List of matching Solution objects
    """
    with get_db_session() as session:
        try:
            query = session.query(db.Solution).filter(db.Solution.name == name)
            if limit is not None:
                query = query.limit(limit)
            solutions = query.all()
            return solutions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching solution: {e}")
            return []


def get_solutions_by_category(category: str) -> list[db.Solution]:
    """
    Retrieve solutions by category.

    Args:
        category: Category to filter by

    Returns:
        List of matching Solution objects
    """
    with get_db_session() as session:
        try:
            solutions = session.query(db.Solution).filter(
                db.Solution.category == category
            ).all()
            return solutions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching solutions by category: {e}")
            return []


def delete_solution(solution_id: int) -> bool:
    """
    Delete a solution by its ID.

    Args:
        solution_id: ID of the solution to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            solution = session.query(db.Solution).filter(db.Solution.id == solution_id).first()
            if solution:
                logger.info(f"Deleting solution with id {solution_id}")
                session.delete(solution)
                session.commit()
                result = True
            else:
                logger.warning(f"Solution with id {solution_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting solution: {e}")
            session.rollback()

    return result


# ============================================================================
# ProspectResearch CRUD Operations
# ============================================================================

def create_or_update_prospect_research(research: db.ProspectResearch) -> bool:
    """
    Create or update prospect research in the database.

    Args:
        research: ProspectResearch object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(research)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # Check if it's a foreign key violation
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key constraint' in error_msg.lower() or 'fkey' in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {e}")
                return False

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(research)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging prospect research: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating prospect research: {e}")
            session.rollback()
            result = False

    return result


def get_all_prospect_research() -> list[db.ProspectResearch]:
    """
    Retrieve all prospect research records from the database.

    Returns:
        List of ProspectResearch objects
    """
    with get_db_session() as session:
        try:
            research = session.query(db.ProspectResearch).all()
            return research
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospect research: {e}")
            return []


def get_prospect_research_by_id(research_id: int) -> db.ProspectResearch | None:
    """
    Retrieve prospect research by its ID.

    Args:
        research_id: ID of the research to retrieve

    Returns:
        ProspectResearch object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            research = session.query(db.ProspectResearch).filter(
                db.ProspectResearch.id == research_id
            ).first()
            return research
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospect research: {e}")
            return None


def get_prospect_research_by_prospect_id(prospect_id: int) -> list[db.ProspectResearch]:
    """
    Retrieve all research records for a specific prospect.

    Args:
        prospect_id: ID of the prospect

    Returns:
        List of ProspectResearch objects for the prospect
    """
    with get_db_session() as session:
        try:
            research = session.query(db.ProspectResearch).filter(
                db.ProspectResearch.prospect_id == prospect_id
            ).all()
            return research
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching prospect research by prospect_id: {e}")
            return []


def delete_prospect_research(research_id: int) -> bool:
    """
    Delete prospect research by its ID.

    Args:
        research_id: ID of the research to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            research = session.query(db.ProspectResearch).filter(
                db.ProspectResearch.id == research_id
            ).first()
            if research:
                logger.info(f"Deleting prospect research with id {research_id}")
                session.delete(research)
                session.commit()
                result = True
            else:
                logger.warning(f"Prospect research with id {research_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting prospect research: {e}")
            session.rollback()

    return result


# ============================================================================
# Interaction CRUD Operations
# ============================================================================

def create_or_update_interaction(interaction: db.Interaction) -> bool:
    """
    Create or update an interaction in the database.

    Args:
        interaction: Interaction object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(interaction)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # Check if it's a foreign key violation
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key constraint' in error_msg.lower() or 'fkey' in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {e}")
                return False

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(interaction)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging interaction: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating interaction: {e}")
            session.rollback()
            result = False

    return result


def get_all_interactions() -> list[db.Interaction]:
    """
    Retrieve all interactions from the database.

    Returns:
        List of Interaction objects
    """
    with get_db_session() as session:
        try:
            interactions = session.query(db.Interaction).all()
            return interactions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching interactions: {e}")
            return []


def get_interaction_by_id(interaction_id: int) -> db.Interaction | None:
    """
    Retrieve an interaction by its ID.

    Args:
        interaction_id: ID of the interaction to retrieve

    Returns:
        Interaction object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            interaction = session.query(db.Interaction).filter(
                db.Interaction.id == interaction_id
            ).first()
            return interaction
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching interaction: {e}")
            return None


def get_interactions_by_prospect_id(prospect_id: int) -> list[db.Interaction]:
    """
    Retrieve all interactions for a specific prospect.

    Args:
        prospect_id: ID of the prospect

    Returns:
        List of Interaction objects for the prospect
    """
    with get_db_session() as session:
        try:
            interactions = session.query(db.Interaction).filter(
                db.Interaction.prospect_id == prospect_id
            ).all()
            return interactions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching interactions by prospect_id: {e}")
            return []


def get_interactions_by_type(interaction_type: db.InteractionType) -> list[db.Interaction]:
    """
    Retrieve interactions by type.

    Args:
        interaction_type: Type of interaction to filter by

    Returns:
        List of Interaction objects of the specified type
    """
    with get_db_session() as session:
        try:
            interactions = session.query(db.Interaction).filter(
                db.Interaction.interaction_type == interaction_type
            ).all()
            return interactions
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching interactions by type: {e}")
            return []


def delete_interaction(interaction_id: int) -> bool:
    """
    Delete an interaction by its ID.

    Args:
        interaction_id: ID of the interaction to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            interaction = session.query(db.Interaction).filter(
                db.Interaction.id == interaction_id
            ).first()
            if interaction:
                logger.info(f"Deleting interaction with id {interaction_id}")
                session.delete(interaction)
                session.commit()
                result = True
            else:
                logger.warning(f"Interaction with id {interaction_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting interaction: {e}")
            session.rollback()

    return result


# ============================================================================
# OutreachDraft CRUD Operations
# ============================================================================

def create_or_update_outreach_draft(draft: db.OutreachDraft) -> bool:
    """
    Create or update an outreach draft in the database.

    Args:
        draft: OutreachDraft object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(draft)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # Check if it's a foreign key violation
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key constraint' in error_msg.lower() or 'fkey' in error_msg.lower():
                logger.error(f"Foreign key constraint violation: {e}")
                return False

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(draft)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging outreach draft: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating outreach draft: {e}")
            session.rollback()
            result = False

    return result


def get_all_outreach_drafts() -> list[db.OutreachDraft]:
    """
    Retrieve all outreach drafts from the database.

    Returns:
        List of OutreachDraft objects
    """
    with get_db_session() as session:
        try:
            drafts = session.query(db.OutreachDraft).all()
            return drafts
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching outreach drafts: {e}")
            return []


def get_outreach_draft_by_id(draft_id: int) -> db.OutreachDraft | None:
    """
    Retrieve an outreach draft by its ID.

    Args:
        draft_id: ID of the draft to retrieve

    Returns:
        OutreachDraft object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            draft = session.query(db.OutreachDraft).filter(
                db.OutreachDraft.id == draft_id
            ).first()
            return draft
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching outreach draft: {e}")
            return None


def get_outreach_drafts_by_prospect_id(prospect_id: int) -> list[db.OutreachDraft]:
    """
    Retrieve all outreach drafts for a specific prospect.

    Args:
        prospect_id: ID of the prospect

    Returns:
        List of OutreachDraft objects for the prospect
    """
    with get_db_session() as session:
        try:
            drafts = session.query(db.OutreachDraft).filter(
                db.OutreachDraft.prospect_id == prospect_id
            ).all()
            return drafts
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching outreach drafts by prospect_id: {e}")
            return []


def get_outreach_drafts_by_status(status: str) -> list[db.OutreachDraft]:
    """
    Retrieve outreach drafts by status.

    Args:
        status: Status to filter by

    Returns:
        List of OutreachDraft objects with the specified status
    """
    with get_db_session() as session:
        try:
            drafts = session.query(db.OutreachDraft).filter(
                db.OutreachDraft.status == status
            ).all()
            return drafts
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching outreach drafts by status: {e}")
            return []


def delete_outreach_draft(draft_id: int) -> bool:
    """
    Delete an outreach draft by its ID.

    Args:
        draft_id: ID of the draft to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            draft = session.query(db.OutreachDraft).filter(
                db.OutreachDraft.id == draft_id
            ).first()
            if draft:
                logger.info(f"Deleting outreach draft with id {draft_id}")
                session.delete(draft)
                session.commit()
                result = True
            else:
                logger.warning(f"Outreach draft with id {draft_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting outreach draft: {e}")
            session.rollback()

    return result


# ============================================================================
# Event CRUD Operations
# ============================================================================

def create_or_update_event(event: db.Event) -> bool:
    """
    Create or update an event in the database.

    Args:
        event: Event object to create or update

    Returns:
        True if successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            session.add(event)
            session.commit()
            result = True
        except exc.IntegrityError as e:
            session.rollback()

            # For unique constraints, try merge
            try:
                logger.info(f"Integrity error, attempting merge: {e}")
                session.merge(event)
                session.commit()
                result = True
            except exc.SQLAlchemyError as merge_error:
                logger.error(f"Error merging event: {merge_error}")
                session.rollback()
                result = False
        except exc.SQLAlchemyError as e:
            logger.error(f"Error creating event: {e}")
            session.rollback()
            result = False

    return result


def get_all_events() -> list[db.Event]:
    """
    Retrieve all events from the database.

    Returns:
        List of Event objects
    """
    with get_db_session() as session:
        try:
            events = session.query(db.Event).all()
            return events
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching events: {e}")
            return []


def get_event_by_id(event_id: int) -> db.Event | None:
    """
    Retrieve an event by its ID.

    Args:
        event_id: ID of the event to retrieve

    Returns:
        Event object if found, None otherwise
    """
    with get_db_session() as session:
        try:
            event = session.query(db.Event).filter(
                db.Event.id == event_id
            ).first()
            return event
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching event: {e}")
            return None


def get_events_by_type(event_type: str) -> list[db.Event]:
    """
    Retrieve events by type.

    Args:
        event_type: Type of event to filter by

    Returns:
        List of Event objects of the specified type
    """
    with get_db_session() as session:
        try:
            events = session.query(db.Event).filter(
                db.Event.event_type == event_type
            ).all()
            return events
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching events by type: {e}")
            return []


def delete_event(event_id: int) -> bool:
    """
    Delete an event by its ID.

    Args:
        event_id: ID of the event to delete

    Returns:
        True if deletion successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            event = session.query(db.Event).filter(db.Event.id == event_id).first()
            if event:
                logger.info(f"Deleting event with id {event_id}")
                session.delete(event)
                session.commit()
                result = True
            else:
                logger.warning(f"Event with id {event_id} not found when deleting.")

        except exc.SQLAlchemyError as e:
            logger.error(f"Error deleting event: {e}")
            session.rollback()

    return result


# ============================================================================
# LLMUsageLog Logging Functions
# ============================================================================

def log_llm_usage(
    workflow_name: str,
    node_name: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    latency_ms: int = 0,
    cost: float = 0.0
) -> bool:
    """
    Log LLM usage to the database.

    Args:
        workflow_name: Name of the workflow
        node_name: Name of the node/step
        model: Model identifier used
        prompt_tokens: Number of prompt tokens used (default: 0)
        completion_tokens: Number of completion tokens used (default: 0)
        total_tokens: Total tokens used (default: 0)
        latency_ms: Latency in milliseconds (default: 0)
        cost: Cost of the operation (default: 0.0)

    Returns:
        True if logging successful, False otherwise
    """
    result = False
    with get_db_session() as session:
        try:
            # Note: Database has typo "worfklow_name" instead of "workflow_name"
            log_entry = db.LLMUsageLog(
                worfklow_name=workflow_name,  # Typo in database schema
                node_name=node_name,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                cost=cost
            )
            session.add(log_entry)
            session.commit()
            result = True
            logger.debug(f"Logged LLM usage: {workflow_name}/{node_name} - {model}")
        except exc.SQLAlchemyError as e:
            logger.error(f"Error logging LLM usage: {e}")
            session.rollback()
            result = False

    return result


def get_llm_usage_logs(
    workflow_name: str | None = None,
    model: str | None = None,
    limit: int | None = None
) -> list[db.LLMUsageLog]:
    """
    Retrieve LLM usage logs with optional filtering.

    Args:
        workflow_name: Optional workflow name to filter by
        model: Optional model to filter by
        limit: Optional limit on number of results

    Returns:
        List of LLMUsageLog objects
    """
    with get_db_session() as session:
        try:
            # Note: Database has typo "worfklow_name" instead of "workflow_name"
            query = session.query(db.LLMUsageLog)

            if workflow_name is not None:
                query = query.filter(db.LLMUsageLog.worfklow_name == workflow_name)

            if model is not None:
                query = query.filter(db.LLMUsageLog.model == model)

            if limit is not None:
                query = query.limit(limit)

            logs = query.all()
            return logs
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching LLM usage logs: {e}")
            return []


def get_llm_usage_stats(workflow_name: str | None = None) -> dict:
    """
    Get aggregated statistics for LLM usage.

    Args:
        workflow_name: Optional workflow name to filter by

    Returns:
        Dictionary with aggregated statistics (total_cost, total_tokens, etc.)
    """
    from sqlalchemy import func

    with get_db_session() as session:
        try:
            # Note: Database has typo "worfklow_name" instead of "workflow_name"
            query = session.query(
                func.count(db.LLMUsageLog.id).label('total_calls'),
                func.sum(db.LLMUsageLog.prompt_tokens).label('total_prompt_tokens'),
                func.sum(db.LLMUsageLog.completion_tokens).label('total_completion_tokens'),
                func.sum(db.LLMUsageLog.total_tokens).label('total_tokens'),
                func.sum(db.LLMUsageLog.cost).label('total_cost'),
                func.avg(db.LLMUsageLog.latency_ms).label('avg_latency_ms')
            )

            if workflow_name is not None:
                query = query.filter(db.LLMUsageLog.worfklow_name == workflow_name)

            result = query.first()

            return {
                'total_calls': result.total_calls or 0,
                'total_prompt_tokens': result.total_prompt_tokens or 0,
                'total_completion_tokens': result.total_completion_tokens or 0,
                'total_tokens': result.total_tokens or 0,
                'total_cost': float(result.total_cost or 0.0),
                'avg_latency_ms': float(result.avg_latency_ms or 0.0)
            }
        except exc.SQLAlchemyError as e:
            logger.error(f"Error fetching LLM usage stats: {e}")
            return {
                'total_calls': 0,
                'total_prompt_tokens': 0,
                'total_completion_tokens': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'avg_latency_ms': 0.0
            }
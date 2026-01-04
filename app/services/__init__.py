"""
Services module for database operations and business logic.
"""

# Database CRUD operations
from .db_crud import (
    get_db_session,
    # Prospect operations
    create_or_update_prospect,
    get_all_prospects,
    get_prospect_by_id,
    get_prospect_by_name,
    delete_prospect,
    # Company operations
    create_or_update_company,
    get_all_companies,
    get_company_by_id,
    get_company_by_name,
    delete_company,
    # Solution operations
    create_or_update_solution,
    get_all_solutions,
    get_solution_by_id,
    get_solution_by_name,
    get_solutions_by_category,
    delete_solution,
    # Prospect Research operations
    create_or_update_prospect_research,
    get_all_prospect_research,
    get_prospect_research_by_id,
    get_prospect_research_by_prospect_id,
    delete_prospect_research,
    # Interaction operations
    create_or_update_interaction,
    get_all_interactions,
    get_interaction_by_id,
    get_interactions_by_prospect_id,
    get_interactions_by_type,
    get_interactions_by_date,
    delete_interaction,
    # Outreach Draft operations
    create_or_update_outreach_draft,
    get_all_outreach_drafts,
    get_outreach_draft_by_id,
    get_outreach_drafts_by_prospect_id,
    get_outreach_drafts_by_status,
    delete_outreach_draft,
    # Event operations
    create_or_update_event,
    get_all_events,
    get_event_by_id,
    get_events_by_type,
    delete_event,
    # LLM Usage operations
    log_llm_usage,
    get_llm_usage_logs,
    get_llm_usage_stats,
)

# Vector CRUD operations
from .db_vector_crud import (
    cosine_distance,
    # Interaction Vector operations
    create_interaction_vector,
    get_interaction_vector_by_id,
    delete_interaction_vector,
    update_interaction_vector,
    # Solution Vector operations
    create_solution_vector,
    get_solution_vector_by_id,
    delete_solution_vector,
    update_solution_vector,
    # Vector search operations
    vector_search_text,
    search_solution_with_filters,
    search_interaction_vector_with_filters,
)

# Vector service operations
from .vector_service import (
    get_embedding,
    chunk_text,
    chunk_and_embed_text,
)

__all__ = [
    # Database session
    "get_db_session",
    # Prospect operations
    "create_or_update_prospect",
    "get_all_prospects",
    "get_prospect_by_id",
    "get_prospect_by_name",
    "delete_prospect",
    # Company operations
    "create_or_update_company",
    "get_all_companies",
    "get_company_by_id",
    "get_company_by_name",
    "delete_company",
    # Solution operations
    "create_or_update_solution",
    "get_all_solutions",
    "get_solution_by_id",
    "get_solution_by_name",
    "get_solutions_by_category",
    "delete_solution",
    # Prospect Research operations
    "create_or_update_prospect_research",
    "get_all_prospect_research",
    "get_prospect_research_by_id",
    "get_prospect_research_by_prospect_id",
    "delete_prospect_research",
    # Interaction operations
    "create_or_update_interaction",
    "get_all_interactions",
    "get_interaction_by_id",
    "get_interactions_by_prospect_id",
    "get_interactions_by_type",
    "get_interactions_by_date",
    "delete_interaction",
    # Outreach Draft operations
    "create_or_update_outreach_draft",
    "get_all_outreach_drafts",
    "get_outreach_draft_by_id",
    "get_outreach_drafts_by_prospect_id",
    "get_outreach_drafts_by_status",
    "delete_outreach_draft",
    # Event operations
    "create_or_update_event",
    "get_all_events",
    "get_event_by_id",
    "get_events_by_type",
    "delete_event",
    # LLM Usage operations
    "log_llm_usage",
    "get_llm_usage_logs",
    "get_llm_usage_stats",
    # Vector utilities
    "cosine_distance",
    # Interaction Vector operations
    "create_interaction_vector",
    "get_interaction_vector_by_id",
    "delete_interaction_vector",
    "update_interaction_vector",
    # Solution Vector operations
    "create_solution_vector",
    "get_solution_vector_by_id",
    "delete_solution_vector",
    "update_solution_vector",
    # Vector search operations
    "vector_search_text",
    "search_solution_with_filters",
    "search_interaction_vector_with_filters",
    # Vector service operations
    "get_embedding",
    "chunk_text",
    "chunk_and_embed_text",
]

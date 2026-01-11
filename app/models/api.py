"""
models/api.py:
Define JSON schemas and pydantic models for API calls.
"""

from pydantic import BaseModel
from datetime import datetime
from database import ProspectStatus, PricingModels, InteractionType
import json


class ProspectCreate(BaseModel):
    full_name: str
    email: str
    company_id: int
    linkedin_url: str | None = None
    location: str | None = None
    last_contacted_at: datetime | None = None
    is_active: bool = True
    status: ProspectStatus = ProspectStatus.NEW


class ProspectUpdate(BaseModel):
    id: int
    full_name: str
    email: str
    company_id: int
    linkedin_url: str | None = None
    location: str | None = None
    last_contacted_at: datetime | None = None
    is_active: bool = True
    status: ProspectStatus = ProspectStatus.NEW


class ProspectResponse(BaseModel):
    id: int
    full_name: str
    email: str
    company_id: int
    linkedin_url: str | None = None
    location: str | None = None
    last_contacted_at: datetime | None = None
    is_active: bool = True
    status: ProspectStatus = ProspectStatus.NEW
    created_at: datetime
    updated_at: datetime


class CompanyCreate(BaseModel):
    name: str
    industry_id: int
    size: str
    website: str | None = None


class CompanyUpdate(BaseModel):
    id: int
    name: str
    industry_id: int
    size: str
    website: str | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry_id: int
    size: str
    website: str | None = None
    created_at: datetime
    updated_at: datetime


class SolutionCreate(BaseModel):
    name: str
    category: str
    description: str
    use_cases: str | None = None
    keywords: str | None = None
    pricing_model: PricingModels = PricingModels.ON_DEMAND


class SolutionUpdate(BaseModel):
    id: int
    name: str
    category: str
    description: str
    use_cases: str | None = None
    keywords: str | None = None
    pricing_model: PricingModels = PricingModels.ON_DEMAND


class SolutionResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str
    use_cases: str | None = None
    keywords: str | None = None
    pricing_model: PricingModels = PricingModels.ON_DEMAND
    created_at: datetime
    updated_at: datetime


class EventCreate(BaseModel):
    event_type: str
    event_date: datetime
    description: str
    location: str
    target_industries: str
    target_roles: str | None = None
    solutions_featured: str | None = None
    status: str


class EventUpdate(BaseModel):
    id: int
    event_type: str
    event_date: datetime
    description: str
    location: str
    target_industries: str
    target_roles: str | None = None
    solutions_featured: str | None = None
    status: str


class EventResponse(BaseModel):
    id: int
    event_type: str
    event_date: datetime
    description: str
    location: str
    target_industries: str
    target_roles: str | None = None
    solutions_featured: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ProspectResearchCreate(BaseModel):
    prospect_id: int
    research_summary: str
    key_insights: str | None = None
    recommended_solutions: str | None = None
    confidence_score: float | None = None


class ProspectResearchUpdate(BaseModel):
    id: int
    prospect_id: int
    research_summary: str
    key_insights: str | None = None
    recommended_solutions: str | None = None
    confidence_score: float | None = None


class ProspectResearchResponse(BaseModel):
    id: int
    prospect_id: int
    research_summary: str
    key_insights: str | None = None
    recommended_solutions: str | None = None
    confidence_score: float | None = None
    created_at: datetime
    updated_at: datetime


class InteractionCreate(BaseModel):
    prospect_id: int
    interaction_type: InteractionType
    event_id: int | None = None
    interaction_date: datetime
    subject: str
    content: str
    sentiment: str | None = None
    outcome: str | None = None


class InteractionUpdate(BaseModel):
    id: int
    prospect_id: int
    interaction_type: InteractionType
    event_id: int | None = None
    interaction_date: datetime
    subject: str
    content: str
    sentiment: str | None = None
    outcome: str | None = None


class InteractionResponse(BaseModel):
    id: int
    prospect_id: int
    interaction_type: InteractionType
    event_id: int | None = None
    interaction_date: datetime
    subject: str
    content: str
    sentiment: str | None = None
    outcome: str | None = None
    created_at: datetime
    updated_at: datetime


class OutreachDraftCreate(BaseModel):
    prospect_id: int
    event_id: int | None = None
    draft_type: str
    content: str
    status: str


class OutreachDraftUpdate(BaseModel):
    id: int
    prospect_id: int
    event_id: int | None = None
    draft_type: str
    content: str
    status: str


class OutreachDraftResponse(BaseModel):
    id: int
    prospect_id: int
    event_id: int | None = None
    draft_type: str
    content: str
    status: str
    created_at: datetime
    updated_at: datetime

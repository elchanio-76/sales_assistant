from sqlalchemy import  Integer, String, ForeignKey, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone
from typing import Optional
import pytz

class Base(DeclarativeBase):
    pass

class Prospect(Base):
    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(255))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")),
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # One to One relationship with Company
    company: Mapped["Company"] = relationship("Company", back_populates="prospects")

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    industry_id: Mapped[int] = mapped_column(ForeignKey("industries.id"))
    size: Mapped[str] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # One-to-One relationship with Industry
    industries: Mapped["Industry"] = relationship("Industry", back_populates="companies")
    # One to many relationship with Prospect
    prospects: Mapped[list["Prospect"]] = relationship("Prospect", back_populates="company")

class Industry(Base):
    __tablename__ = "industries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # One-to-many relationship with Company
    companies: Mapped[list["Company"]] = relationship("Company", back_populates="industries")
    industry_solutions: Mapped[list["IndustrySolution"]] = relationship("IndustrySolution", back_populates="industries")

class IndustrySolution(Base): # Reationship Table
    __tablename__ = "industry_solutions"
    # Use a composite primary key to avoid duplicate entries
    industry_id: Mapped[int] = mapped_column(ForeignKey("industries.id"), primary_key=True)
    solution_id: Mapped[int] = mapped_column(ForeignKey("solutions.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    industries: Mapped["Industry"] = relationship("Industry", back_populates="industry_solutions")
    solutions: Mapped["Solution"] = relationship("Solution", back_populates="industries")

class Solution(Base):
    __tablename__ = "solutions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(255))   # TODO: Change to enum
    description: Mapped[str] = mapped_column(Text)
    use_cases: Mapped[JSONB] = mapped_column(JSONB, nullable=True)
    keywords: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    pricing_model: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # One-to-many relationship with IndustrySOlutions
    industry_solutions: Mapped[list["IndustrySolution"]] = relationship("industry_solutions", back_populates="solutions")

class ProspectResearch(Base):
    __tablename__ = "prospect_research"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id"))
    research_summary: Mapped[str] = mapped_column(Text)
    key_insights: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    recommended_solutions: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # Many-to-one relationship with Prospect
    prospect: Mapped["Prospect"] = relationship("Prospect")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    event_date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(255))
    target_industries: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    target_roles: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True) 
    solutions_featured: Mapped[Optional[JSONB]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    
    
class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id"))
    event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id"), nullable=True)
    interaction_type: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    interaction_date: Mapped[datetime] = mapped_column(DateTime)
    subject: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    sentiment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)    
    outcome: Mapped[Optional[Text]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # Many-to-one relationship with Prospect
    prospect: Mapped["Prospect"] = relationship("Prospect")

class OutreachDraft(Base):
    __tablename__ = "outreach_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id"))
    event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id"), nullable=True)
    draft_type: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(255))  # TODO: Change to enum
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    # Many-to-one relationship with Prospect
    prospect: Mapped["Prospect"] = relationship("Prospect")

class LLMUsageLog:
    __tablename__ = "llm_usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worfklow_name: Mapped[str] = mapped_column(String(255))
    node_name: Mapped[str] = mapped_column(String(255))
    model: Mapped[str] = mapped_column(String(255))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.now(tz= pytz.timezone("Europe/Athens")), 
        onupdate=datetime.now(tz= pytz.timezone("Europe/Athens"))
    )


def main():
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base

    engine = create_engine("postgresql://postgres:postgres@localhost:5432/sales_test", echo = True)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()
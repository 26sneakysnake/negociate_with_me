# backend/db_models.py
from sqlalchemy import Column, String, Text, DateTime, JSON, Float, Integer
from sqlalchemy.sql import func
from database import Base
import uuid

class NegotiationSessionDB(Base):
    __tablename__ = "negotiation_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Context
    context_text = Column(Text, nullable=False)
    objective = Column(String, nullable=False)
    minimum_acceptable = Column(String, nullable=False)
    counterparty_name = Column(String, nullable=True)
    deadline = Column(String, nullable=True)

    # Strategy (JSON)
    strategy_json = Column(JSON, nullable=True)

    # Analysis (JSON)
    analysis_json = Column(JSON, nullable=True)

    # Performance scores for quick queries
    overall_score = Column(Float, nullable=True)
    preparation_score = Column(Float, nullable=True)
    tactics_score = Column(Float, nullable=True)
    outcome_score = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Template used (if any)
    template_used = Column(String, nullable=True)

class ContextTemplate(Base):
    __tablename__ = "context_templates"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # saas, immobilier, salaire
    description = Column(Text, nullable=False)
    context_template = Column(Text, nullable=False)
    objective_template = Column(String, nullable=False)
    minimum_template = Column(String, nullable=False)
    icon = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

# backend/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Request Models
class NegotiationContext(BaseModel):
    """Input: User's negotiation context"""
    context_text: str = Field(..., description="Contract or briefing text")
    objective: str = Field(..., description="Main goal (e.g., '50K€ annual contract')")
    minimum_acceptable: str = Field(..., description="Walk-away point")
    counterparty_name: Optional[str] = Field(None, description="Company/person name")
    deadline: Optional[str] = Field(None, description="When negotiation happens")

class TranscriptAnalysis(BaseModel):
    """Input: Post-negotiation transcript"""
    session_id: str
    transcript: str = Field(..., description="Full conversation transcript")
    actual_outcome: str = Field(..., description="What was achieved")

# Response Models
class Objection(BaseModel):
    """A potential objection from counterparty"""
    objection: str
    counter_argument: str
    confidence: float = Field(ge=0, le=1)

class Strategy(BaseModel):
    """Generated negotiation strategy"""
    session_id: str
    summary: str
    opening_position: str
    key_arguments: List[str]
    concession_plan: List[str]
    red_lines: List[str]
    expected_objections: List[Objection]
    batna: str = Field(..., description="Best Alternative To Negotiated Agreement")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TacticDetection(BaseModel):
    """A detected negotiation tactic in transcript"""
    tactic_name: str
    tactic_type: Literal["offensive", "defensive", "neutral"]
    quote: str = Field(..., description="Exact phrase from transcript")
    effectiveness: Literal["excellent", "good", "poor", "missed_opportunity"]
    explanation: str

class PerformanceScore(BaseModel):
    """Overall performance metrics"""
    overall_score: float = Field(ge=0, le=100)
    preparation_score: float = Field(ge=0, le=100)
    tactics_score: float = Field(ge=0, le=100)
    outcome_score: float = Field(ge=0, le=100)

class Analysis(BaseModel):
    """Post-negotiation analysis"""
    session_id: str
    performance: PerformanceScore
    tactics_used: List[TacticDetection]
    strengths: List[str]
    weaknesses: List[str]
    key_recommendations: List[str]
    audio_url: Optional[str] = Field(None, description="Generated feedback audio")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Storage Models
class Session(BaseModel):
    """Persistent session data"""
    id: str
    context: NegotiationContext
    strategy: Optional[Strategy] = None
    analysis: Optional[Analysis] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

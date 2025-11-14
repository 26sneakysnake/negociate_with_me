# backend/crud.py
from sqlalchemy.orm import Session
from db_models import NegotiationSessionDB, ContextTemplate
from models import NegotiationContext, Strategy, Analysis
from typing import List, Optional
import json

def create_session(db: Session, context: NegotiationContext, session_id: str, template_used: Optional[str] = None) -> NegotiationSessionDB:
    """Create a new negotiation session in DB"""
    db_session = NegotiationSessionDB(
        id=session_id,
        context_text=context.context_text,
        objective=context.objective,
        minimum_acceptable=context.minimum_acceptable,
        counterparty_name=context.counterparty_name,
        deadline=context.deadline,
        template_used=template_used
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_session_strategy(db: Session, session_id: str, strategy: Strategy) -> NegotiationSessionDB:
    """Update session with generated strategy"""
    db_session = db.query(NegotiationSessionDB).filter(NegotiationSessionDB.id == session_id).first()
    if db_session:
        db_session.strategy_json = strategy.model_dump(mode='json')  # Pydantic v2 with JSON serialization
        db.commit()
        db.refresh(db_session)
        print(f"✅ Strategy saved for session {session_id}")
    else:
        print(f"⚠️ Session {session_id} not found in database")
    return db_session

def update_session_analysis(db: Session, session_id: str, analysis: Analysis, transcript: str, actual_outcome: str) -> NegotiationSessionDB:
    """Update session with analysis results"""
    db_session = db.query(NegotiationSessionDB).filter(NegotiationSessionDB.id == session_id).first()
    if db_session:
        db_session.analysis_json = analysis.model_dump(mode='json')  # Pydantic v2 with JSON serialization
        db_session.transcript = transcript
        db_session.actual_outcome = actual_outcome
        db_session.overall_score = analysis.performance.overall_score
        db_session.preparation_score = analysis.performance.preparation_score
        db_session.tactics_score = analysis.performance.tactics_score
        db_session.outcome_score = analysis.performance.outcome_score
        db.commit()
        db.refresh(db_session)
        print(f"✅ Analysis saved for session {session_id}")
    else:
        print(f"⚠️ Session {session_id} not found in database")
    return db_session

def get_session(db: Session, session_id: str) -> Optional[NegotiationSessionDB]:
    """Get a session by ID"""
    return db.query(NegotiationSessionDB).filter(NegotiationSessionDB.id == session_id).first()

def get_all_sessions(db: Session, limit: int = 50, offset: int = 0) -> List[NegotiationSessionDB]:
    """Get all sessions ordered by most recent"""
    return db.query(NegotiationSessionDB)\
        .order_by(NegotiationSessionDB.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()

def get_sessions_with_analysis(db: Session, limit: int = 10) -> List[NegotiationSessionDB]:
    """Get sessions that have analysis (for performance comparison)"""
    return db.query(NegotiationSessionDB)\
        .filter(NegotiationSessionDB.analysis_json.isnot(None))\
        .order_by(NegotiationSessionDB.created_at.desc())\
        .limit(limit)\
        .all()

def get_all_templates(db: Session) -> List[ContextTemplate]:
    """Get all context templates"""
    return db.query(ContextTemplate).all()

def get_template(db: Session, template_id: str) -> Optional[ContextTemplate]:
    """Get a specific template"""
    return db.query(ContextTemplate).filter(ContextTemplate.id == template_id).first()

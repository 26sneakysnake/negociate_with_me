# backend/routers/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Strategy, Analysis, NegotiationContext
import crud
from services.pdf_service import PDFService
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
pdf_service = PDFService()

# Response models
class SessionListItem(BaseModel):
    id: str
    objective: str
    context_text: str
    actual_outcome: str | None
    counterparty_name: str | None
    created_at: datetime
    overall_score: float | None
    preparation_score: float | None
    tactics_score: float | None
    outcome_score: float | None
    has_strategy: bool
    has_analysis: bool
    template_used: str | None

class SessionDetail(BaseModel):
    id: str
    context_text: str
    objective: str
    minimum_acceptable: str
    counterparty_name: str | None
    deadline: str | None
    strategy_json: dict | None
    analysis_json: dict | None
    overall_score: float | None
    preparation_score: float | None
    tactics_score: float | None
    outcome_score: float | None
    created_at: datetime
    template_used: str | None

class PerformanceStats(BaseModel):
    session_id: str
    created_at: datetime
    overall_score: float
    preparation_score: float
    tactics_score: float
    outcome_score: float

@router.get("/", response_model=List[SessionListItem])
async def list_sessions(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Get list of all negotiation sessions"""
    sessions = crud.get_all_sessions(db, limit=limit, offset=offset)

    return [
        SessionListItem(
            id=s.id,
            objective=s.objective,
            context_text=s.context_text,
            actual_outcome=s.actual_outcome,
            counterparty_name=s.counterparty_name,
            created_at=s.created_at,
            overall_score=s.overall_score,
            preparation_score=s.preparation_score,
            tactics_score=s.tactics_score,
            outcome_score=s.outcome_score,
            has_strategy=s.strategy_json is not None,
            has_analysis=s.analysis_json is not None,
            template_used=s.template_used
        )
        for s in sessions
    ]

@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific session"""
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetail(
        id=session.id,
        context_text=session.context_text,
        objective=session.objective,
        minimum_acceptable=session.minimum_acceptable,
        counterparty_name=session.counterparty_name,
        deadline=session.deadline,
        strategy_json=session.strategy_json,
        analysis_json=session.analysis_json,
        overall_score=session.overall_score,
        preparation_score=session.preparation_score,
        tactics_score=session.tactics_score,
        outcome_score=session.outcome_score,
        created_at=session.created_at,
        template_used=session.template_used
    )

@router.get("/performance/history", response_model=List[PerformanceStats])
async def get_performance_history(limit: int = 10, db: Session = Depends(get_db)):
    """Get performance history for comparison charts"""
    sessions = crud.get_sessions_with_analysis(db, limit=limit)

    return [
        PerformanceStats(
            session_id=s.id,
            created_at=s.created_at,
            overall_score=s.overall_score,
            preparation_score=s.preparation_score,
            tactics_score=s.tactics_score,
            outcome_score=s.outcome_score
        )
        for s in sessions
        if s.overall_score is not None
    ]

@router.get("/{session_id}/export/strategy")
async def export_strategy_pdf(session_id: str, db: Session = Depends(get_db)):
    """Export strategy as PDF"""
    session = crud.get_session(db, session_id)
    if not session or not session.strategy_json:
        raise HTTPException(status_code=404, detail="Strategy not found")

    try:
        # Reconstruct objects
        from models import Strategy, NegotiationContext
        strategy = Strategy(**session.strategy_json)
        context = NegotiationContext(
            context_text=session.context_text,
            objective=session.objective,
            minimum_acceptable=session.minimum_acceptable,
            counterparty_name=session.counterparty_name,
            deadline=session.deadline
        )

        # Generate PDF
        filename = f"strategy_{session_id}.pdf"
        filepath = await pdf_service.generate_strategy_pdf(strategy, context, filename)

        return FileResponse(
            filepath,
            media_type="application/pdf",
            filename=f"negotiation_strategy_{session_id[:8]}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@router.get("/{session_id}/export/analysis")
async def export_analysis_pdf(session_id: str, db: Session = Depends(get_db)):
    """Export analysis as PDF"""
    session = crud.get_session(db, session_id)
    if not session or not session.analysis_json or not session.strategy_json:
        raise HTTPException(status_code=404, detail="Analysis not found")

    try:
        # Reconstruct objects
        from models import Analysis, Strategy
        analysis = Analysis(**session.analysis_json)
        strategy = Strategy(**session.strategy_json)

        # Generate PDF
        filename = f"analysis_{session_id}.pdf"
        filepath = await pdf_service.generate_analysis_pdf(analysis, strategy, filename)

        return FileResponse(
            filepath,
            media_type="application/pdf",
            filename=f"negotiation_analysis_{session_id[:8]}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

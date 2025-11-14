# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session as DBSession
from config import get_settings
from models import (
    NegotiationContext, Strategy, TranscriptAnalysis, Analysis, Session
)
from services.mistral_service import MistralService
from services.qdrant_service import QdrantService
from services.elevenlabs_service import ElevenLabsService
from database import get_db, Base, engine
import crud
from routers.sessions import router as sessions_router
from routers.templates import router as templates_router
from typing import Dict, Optional
import PyPDF2
import io
import json
import os

# Initialize FastAPI
app = FastAPI(title="NegotiAI v0")
settings = get_settings()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for audio and exports
os.makedirs("audio_files", exist_ok=True)
os.makedirs("exports", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")

# Services - Initialize lazily to allow app to start even with missing API keys
mistral = None
qdrant = None
elevenlabs = None

def init_services():
    """Initialize services with error handling"""
    global mistral, qdrant, elevenlabs
    try:
        mistral = MistralService()
        print("✅ Mistral service initialized")
    except Exception as e:
        print(f"⚠️ Mistral service failed to initialize: {e}")

    try:
        qdrant = QdrantService()
        print("✅ Qdrant service initialized")
    except Exception as e:
        print(f"⚠️ Qdrant service failed to initialize: {e}")

    try:
        elevenlabs = ElevenLabsService()
        print("✅ ElevenLabs service initialized")
    except Exception as e:
        print(f"⚠️ ElevenLabs service failed to initialize: {e}")

# In-memory session storage (use Redis in production)
sessions: Dict[str, Session] = {}

# Include routers
app.include_router(sessions_router)
app.include_router(templates_router)

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize services and database"""
    print("\n" + "="*70)
    print("🚀 Starting NegotiAI v0 Backend")
    print("="*70)

    # Database should already be initialized by start.sh
    # This is just a safety check
    print("📦 Checking database connection...")
    try:
        from database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        print("✅ Database connection OK")
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        print("   Backend will continue but database features may not work")

    # Initialize services
    init_services()

    # Try to initialize Qdrant collection and load tactics
    if qdrant is not None:
        try:
            await qdrant.initialize_collection()
            count = await qdrant.load_tactics_database("data/negotiation_tactics.json")
            print(f"✅ Loaded {count} negotiation tactics into Qdrant")
        except Exception as e:
            print(f"⚠️ Could not load tactics: {e}")
    else:
        print("⚠️ Qdrant not available - tactics will not be loaded")

    print("="*70)
    print("✅ Backend is ready!")
    print("="*70 + "\n")

@app.get("/")
async def root():
    return {"message": "NegotiAI v0 API", "status": "running"}

@app.post("/api/upload-context")
async def upload_context(file: UploadFile = File(...)):
    """Extract text from PDF context file"""
    try:
        content = await file.read()

        if file.filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        else:
            text = content.decode('utf-8')

        return {"text": text, "filename": file.filename}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@app.post("/api/generate-strategy", response_model=Strategy)
async def generate_strategy(context: NegotiationContext, db: DBSession = Depends(get_db)):
    """Generate negotiation strategy from context"""
    # Check if required services are available
    if mistral is None:
        raise HTTPException(
            status_code=503,
            detail="Mistral AI service not available. Please check API key configuration."
        )

    try:
        # Embed the context to find relevant tactics
        relevant_tactics = []
        if qdrant is not None:
            try:
                context_embedding = mistral.embed_text(
                    f"{context.objective} {context.context_text[:500]}"
                )
                relevant_tactics = await qdrant.search_relevant_tactics(
                    context_embedding,
                    limit=10
                )
            except Exception as e:
                print(f"⚠️ Could not retrieve tactics from Qdrant: {e}")
                # Continue without tactics

        # Generate strategy
        strategy = await mistral.generate_strategy(
            context_text=context.context_text,
            objective=context.objective,
            minimum=context.minimum_acceptable,
            counterparty=context.counterparty_name or "Unknown",
            tactics_context=relevant_tactics
        )

        # Store session in-memory (for backward compatibility)
        session = Session(
            id=strategy.session_id,
            context=context,
            strategy=strategy
        )
        sessions[strategy.session_id] = session

        # Persist to database
        try:
            crud.create_session(
                db=db,
                session_id=strategy.session_id,
                context=context
            )
            crud.update_session_strategy(
                db=db,
                session_id=strategy.session_id,
                strategy=strategy
            )
            print(f"✅ Session {strategy.session_id} saved to database")
        except Exception as e:
            print(f"⚠️ Could not save session to database: {e}")
            # Continue anyway - in-memory session still works

        return strategy

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating strategy: {str(e)}")

@app.post("/api/analyze-negotiation", response_model=Analysis)
async def analyze_negotiation(analysis_input: TranscriptAnalysis, db: DBSession = Depends(get_db)):
    """Analyze negotiation transcript"""
    # Check if required services are available
    if mistral is None:
        raise HTTPException(
            status_code=503,
            detail="Mistral AI service not available. Please check API key configuration."
        )

    try:
        # Get session from in-memory or database
        session = sessions.get(analysis_input.session_id)
        if not session or not session.strategy:
            # Try to load from database
            db_session = crud.get_session(db, analysis_input.session_id)
            if not db_session or not db_session.strategy_json:
                raise HTTPException(status_code=404, detail="Session or strategy not found")
            # Reconstruct session from database
            session = Session(
                id=db_session.id,
                context=NegotiationContext(**db_session.context_json),
                strategy=Strategy(**db_session.strategy_json)
            )
            sessions[analysis_input.session_id] = session

        # Embed transcript to find relevant tactics
        relevant_tactics = []
        if qdrant is not None:
            try:
                print("🔍 Attempting to retrieve relevant tactics...")
                transcript_embedding = mistral.embed_text(analysis_input.transcript[:1000])
                relevant_tactics = await qdrant.search_relevant_tactics(
                    transcript_embedding,
                    limit=15
                )
                print(f"✅ Retrieved {len(relevant_tactics)} tactics")
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ Could not retrieve tactics: {error_msg}")
                # Check if it's a rate limit - inform user but continue
                if "rate limit" in error_msg.lower() or "429" in error_msg:
                    print("ℹ️ Continuing analysis without tactics (rate limit hit)")
                # Continue without tactics - analysis can still work

        # Analyze performance
        print("🧠 Analyzing negotiation performance...")
        try:
            analysis = await mistral.analyze_negotiation(
                strategy=session.strategy,
                transcript=analysis_input.transcript,
                actual_outcome=analysis_input.actual_outcome,
                tactics_context=relevant_tactics
            )
            print("✅ Analysis completed successfully")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Analysis failed: {error_msg}")
            # Re-raise with more context
            if "rate limit" in error_msg.lower() or "429" in error_msg:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please wait a moment and try again. Mistral AI has strict rate limits on free tier."
                )
            raise

        # Generate audio feedback (optional)
        if elevenlabs is not None:
            try:
                feedback_text = elevenlabs.format_analysis_for_speech(analysis)
                audio_file = await elevenlabs.generate_feedback_audio(
                    feedback_text,
                    f"{analysis_input.session_id}.mp3"
                )
                analysis.audio_url = f"/audio/{analysis_input.session_id}.mp3"
            except Exception as e:
                print(f"⚠️ Could not generate audio feedback: {e}")
                # Continue without audio

        # Update session in-memory
        session.analysis = analysis

        # Persist to database
        try:
            crud.update_session_analysis(
                db=db,
                session_id=analysis_input.session_id,
                analysis=analysis,
                transcript=analysis_input.transcript,
                actual_outcome=analysis_input.actual_outcome
            )
            print(f"✅ Analysis for session {analysis_input.session_id} saved to database")
        except Exception as e:
            print(f"⚠️ Could not save analysis to database: {e}")
            # Continue anyway - in-memory session still works

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing negotiation: {str(e)}")

@app.get("/api/session/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session data"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, WebSocket
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

# Import new simulation modules
from audio.elevenlabs_client import ElevenLabsVoiceAgent
from ai.realtime_analyzer import RealtimeAnalyzer
from websocket_handler import handle_simulation_websocket
from services.web_research_service import WebResearchService
from services.elevenlabs_agent_service import ElevenLabsConversationalAgent

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

# New services for real-time simulation
elevenlabs_voice_agent = None
realtime_analyzer = None
web_research_service = None
elevenlabs_conversational_agent = None

def init_services():
    """Initialize services with error handling"""
    global mistral, qdrant, elevenlabs, elevenlabs_voice_agent, realtime_analyzer, web_research_service, elevenlabs_conversational_agent
    try:
        mistral = MistralService()
        print("✅ Mistral service initialized")
    except ValueError as e:
        print(f"\n{'='*70}")
        print(f"❌ MISTRAL SERVICE NOT AVAILABLE")
        print(f"{'='*70}")
        print(f"   Reason: {e}")
        print(f"   Impact: Research, strategy, and opponent AI will NOT work")
        print(f"   Solution: See API_KEYS_SETUP.md for configuration instructions")
        print(f"{'='*70}\n")
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

    # Initialize new simulation services
    try:
        if settings.ELEVENLABS_API_KEY:
            elevenlabs_voice_agent = ElevenLabsVoiceAgent(api_key=settings.ELEVENLABS_API_KEY)
            print("✅ ElevenLabs Voice Agent initialized")
        else:
            print("⚠️ ElevenLabs Voice Agent: No API key provided")
    except Exception as e:
        print(f"⚠️ ElevenLabs Voice Agent failed to initialize: {e}")

    try:
        if settings.MISTRAL_API_KEY:
            realtime_analyzer = RealtimeAnalyzer(
                mistral_key=settings.MISTRAL_API_KEY,
                qdrant_url=settings.QDRANT_URL if hasattr(settings, 'QDRANT_URL') else None,
                qdrant_key=settings.QDRANT_API_KEY if hasattr(settings, 'QDRANT_API_KEY') else None
            )
            print("✅ Realtime Analyzer initialized")
        else:
            print("⚠️ Realtime Analyzer: No Mistral API key provided")
    except Exception as e:
        print(f"⚠️ Realtime Analyzer failed to initialize: {e}")

    # Initialize web research service
    try:
        if mistral:
            web_research_service = WebResearchService(mistral)
            print("✅ Web Research Service initialized")
        else:
            print("⚠️ Web Research Service: Mistral not available")
    except Exception as e:
        print(f"⚠️ Web Research Service failed to initialize: {e}")

    # Initialize ElevenLabs Conversational AI service
    try:
        if settings.ELEVENLABS_API_KEY:
            elevenlabs_conversational_agent = ElevenLabsConversationalAgent(api_key=settings.ELEVENLABS_API_KEY)
            print("✅ ElevenLabs Conversational AI initialized")
        else:
            print("⚠️ ElevenLabs Conversational AI: No API key provided")
    except ValueError as e:
        print(f"\n{'='*70}")
        print(f"❌ ELEVENLABS CONVERSATIONAL AI NOT AVAILABLE")
        print(f"{'='*70}")
        print(f"   Reason: {e}")
        print(f"   Impact: Voice-to-voice conversation will NOT work")
        print(f"   Workaround: Use TEXT mode instead of VOICE mode")
        print(f"   Solution: See API_KEYS_SETUP.md for configuration instructions")
        print(f"{'='*70}\n")
    except Exception as e:
        print(f"⚠️ ElevenLabs Conversational AI failed to initialize: {e}")

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
                context=context,
                session_id=strategy.session_id
            )
            crud.update_session_strategy(
                db=db,
                session_id=strategy.session_id,
                strategy=strategy
            )
            print(f"✅ Session {strategy.session_id} saved to database")
        except Exception as e:
            print(f"⚠️ Could not save session to database: {e}")
            print(f"   Error details: {type(e).__name__}: {e}")
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


# ============================================================================
# REAL-TIME VOICE SIMULATION ENDPOINTS (NEW)
# ============================================================================

@app.post("/api/simulation/research")
async def research_negotiation(request: dict):
    """
    Research product and client before simulation using Mistral AI

    Args:
        request: {
            "product_name": str,
            "company_name": str (optional),
            "industry": str (optional)
        }

    Returns:
        {
            "product": {
                "name": str,
                "features": List[str],
                "typical_pricing": str,
                "competitors": List[str],
                "market_position": str,
                "key_benefits": List[str]
            },
            "client": {
                "name": str,
                "company_size": str,
                "industry": str,
                "pain_points": List[str],
                "budget_range": str,
                "decision_factors": List[str]
            } (optional)
        }
    """

    if not web_research_service:
        raise HTTPException(
            status_code=503,
            detail="Web Research Service not available. Check Mistral API key configuration."
        )

    try:
        product_name = request.get("product_name")
        company_name = request.get("company_name")
        industry = request.get("industry")

        if not product_name:
            raise HTTPException(status_code=400, detail="product_name is required")

        # Perform research
        enriched_context = await web_research_service.prepare_negotiation_context(
            product_name=product_name,
            company_name=company_name,
            industry=industry
        )

        return enriched_context

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during research: {str(e)}")


@app.post("/api/simulation/setup")
async def setup_simulation(context: dict):
    """
    Setup voice simulation session with ElevenLabs Conversational AI

    Args:
        context: {
            "product": str,
            "target_price": str,
            "minimum_price": str,
            "value_props": List[str],
            "opponent_goal": str,
            "research_data": dict (optional - from /api/simulation/research)
        }

    Returns:
        {
            "status": "ready",
            "agent_id": str,
            "conversation_id": str,
            "websocket_url": str,
            "message": str
        }
    """

    if not elevenlabs_conversational_agent:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs Conversational AI not available. Check API key configuration."
        )

    try:
        research_data = context.get("research_data")

        # Create negotiation agent using ElevenLabs Conversational AI
        agent_config = await elevenlabs_conversational_agent.create_negotiation_agent(
            context=context,
            research_data=research_data
        )

        return {
            "status": "ready",
            "agent_id": agent_config["agent_id"],
            "conversation_id": agent_config["conversation_id"],
            "websocket_url": agent_config["websocket_url"],
            "message": "ElevenLabs Conversational AI agent ready for voice simulation"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up simulation: {str(e)}")


@app.websocket("/ws/simulation")
async def simulation_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice simulation

    Client should first send simulation context, then audio chunks or transcripts

    Message types from client:
        - {"type": "start", "context": {...}} - Start simulation
        - {"type": "audio", "audio": "base64...", "text": "..."} - User audio/text
        - {"type": "transcript", "text": "..."} - User transcript only
        - {"type": "autopilot_toggle", "enabled": bool} - Toggle auto-pilot
        - {"type": "autopilot_activate", "tactic": str} - Activate auto-pilot
        - {"type": "stop"} - Stop simulation

    Message types to client:
        - {"type": "status", "message": str} - Status updates
        - {"type": "transcript", "speaker": str, "text": str, "turn": int} - Transcript
        - {"type": "opponent_audio", "audio": "base64...", "format": "mp3"} - Audio from opponent
        - {"type": "suggestion", "suggestion": str, "priority": str, "tactic": str, ...} - Tactical suggestion
        - {"type": "autopilot_audio", "audio": "base64...", "tactic": str} - Auto-pilot response
        - {"type": "summary", "data": {...}} - Session summary
        - {"type": "error", "message": str} - Error message
    """

    if not elevenlabs_voice_agent or not realtime_analyzer:
        await websocket.close(code=1008, reason="Services not available")
        return

    await websocket.accept()

    try:
        # Wait for initial context
        init_data = await websocket.receive_json()

        if init_data.get("type") != "start":
            await websocket.send_json({
                "type": "error",
                "message": "First message must be {type: 'start', context: {...}}"
            })
            await websocket.close()
            return

        context = init_data.get("context", {})

        # Handle the simulation session
        await handle_simulation_websocket(
            websocket=websocket,
            elevenlabs_agent=elevenlabs_voice_agent,
            realtime_analyzer=realtime_analyzer,
            context=context
        )

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

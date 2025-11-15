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
from calls.phone_handler import PhoneCallHandler, get_available_scenarios
from calls.call_analytics import analyze_negotiation_performance
import uuid

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
phone_call_handler = None

# In-memory storage for phone call sessions (use Redis in production)
call_sessions: Dict[str, Dict] = {}

def init_services():
    """Initialize services with error handling"""
    global mistral, qdrant, elevenlabs, elevenlabs_voice_agent, realtime_analyzer, web_research_service, elevenlabs_conversational_agent, phone_call_handler
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

    # Initialize Phone Call Handler
    try:
        if settings.ELEVENLABS_API_KEY:
            phone_call_handler = PhoneCallHandler(
                elevenlabs_api_key=settings.ELEVENLABS_API_KEY,
                agent_phone_number_id=settings.ELEVENLABS_AGENT_PHONE_NUMBER_ID if settings.ELEVENLABS_AGENT_PHONE_NUMBER_ID else None,
                webhook_base_url=settings.WEBHOOK_BASE_URL if hasattr(settings, 'WEBHOOK_BASE_URL') else None
            )
            if settings.ELEVENLABS_AGENT_PHONE_NUMBER_ID:
                print("✅ Phone Call Handler initialized (with phone number)")
            else:
                print("✅ Phone Call Handler initialized (phone calls may not work - missing agent_phone_number_id)")
        else:
            print("⚠️ Phone Call Handler: No ElevenLabs API key provided")
    except Exception as e:
        print(f"⚠️ Phone Call Handler failed to initialize: {e}")


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


# ============================================================================
# PHONE CALL ENDPOINTS (NEW - Real phone calls with ElevenLabs)
# ============================================================================

@app.post("/api/call/test")
async def test_elevenlabs_call(data: dict):
    """
    TEST ENDPOINT - Send a simple test call to verify ElevenLabs configuration

    Request:
    {
        "phone_number": "+33612345678"
    }

    This will send a simple test call using ElevenLabs Conversational AI
    """
    if not phone_call_handler:
        raise HTTPException(status_code=503, detail="Phone Call Handler not available")

    if not phone_call_handler.agent_phone_number_id:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs agent_phone_number_id not configured. Please check ELEVENLABS_AGENT_PHONE_NUMBER_ID in .env"
        )

    try:
        phone_number = data.get("phone_number")
        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")

        print(f"\n{'='*70}")
        print(f"📞 TEST CALL VIA ELEVENLABS")
        print(f"{'='*70}")
        print(f"   To: {phone_number}")
        print(f"   Agent Phone Number ID: {phone_call_handler.agent_phone_number_id}")
        print(f"{'='*70}\n")

        # Create test agent with simple prompt
        test_prompt = """Vous êtes un assistant vocal de test pour NegotiAI.

Dites simplement : "Bonjour ! Ceci est un test de l'application NegotiAI. Si vous recevez cet appel, cela signifie que la configuration fonctionne correctement. Merci et à bientôt !"

Puis raccrochez poliment."""

        print("📝 Creating test agent...")
        agent = phone_call_handler.client.conversational_ai.create_agent(
            conversation_config={
                "agent": {
                    "prompt": {
                        "prompt": test_prompt
                    },
                    "first_message": "Bonjour ! Ceci est un test de NegotiAI.",
                    "language": "fr"
                },
                "tts": {
                    "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                    "model_id": "eleven_turbo_v2_5"
                }
            }
        )

        print(f"✅ Test agent created: {agent.agent_id}")

        # Initiate call using ElevenLabs
        print(f"📞 Initiating call...")
        result = await phone_call_handler.initiate_call(
            phone_number=phone_number,
            agent_id=agent.agent_id
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        print(f"✅ Test call initiated!\n")

        return {
            "status": "success",
            "message": result.get("message", "Test call initiated successfully"),
            "agent_id": agent.agent_id,
            "call_id": result.get("call_id"),
            "to": phone_number
        }

    except Exception as e:
        print(f"❌ Test call failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Test call error: {str(e)}")


@app.get("/api/call/scenarios")
async def get_scenarios():
    """
    Get available negotiation scenarios for phone calls

    Returns:
        {
            "saas": {"name": "...", "description": "..."},
            "freelance": {...},
            ...
        }
    """
    return get_available_scenarios()


@app.post("/api/call/setup")
async def setup_call(data: dict):
    """
    Setup phone call session with AI negotiation opponent

    Request body:
    {
        "scenario": "saas" | "freelance" | "salary" | "partnership" | "real_estate",
        "context": {
            "product": str,
            "target_price": str,
            "minimum_price": str,
            "red_lines": List[str],
            ...
        }
    }

    Returns:
        {
            "session_id": str,
            "scenario": str,
            "ready": bool
        }
    """

    if not phone_call_handler:
        raise HTTPException(
            status_code=503,
            detail="Phone Call Handler not available. Check ElevenLabs API key configuration."
        )

    try:
        scenario_type = data.get("scenario")
        user_context = data.get("context", {})

        if not scenario_type:
            raise HTTPException(status_code=400, detail="scenario is required")

        # Perform Mistral research if company_name is provided
        research_data = None
        company_name = user_context.get("company_name")

        if company_name and web_research_service:
            print(f"🔍 Performing Mistral research on: {company_name}")
            try:
                research_result = await web_research_service.research_company(company_name)
                if research_result and research_result.get("status") == "success":
                    research_data = {
                        "company_info": {
                            "name": company_name,
                            "industry": research_result.get("industry", "Non identifié"),
                            "size": research_result.get("size", "Non identifiée"),
                            "context": research_result.get("summary", "Information non disponible"),
                            "pain_points": research_result.get("pain_points", [])
                        }
                    }
                    print(f"✅ Research completed: {research_data['company_info']['industry']}")
            except Exception as e:
                print(f"⚠️ Research failed: {e}")
                # Continue without research data

        # Create agent configuration for this scenario with research data
        agent_config = await phone_call_handler.create_agent(
            scenario_type=scenario_type,
            user_context=user_context,
            research_data=research_data
        )

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Store session
        call_sessions[session_id] = {
            "agent_config": agent_config,
            "scenario": scenario_type,
            "context": user_context,
            "research_data": research_data,
            "status": "ready",
            "created_at": str(uuid.uuid1())
        }

        print(f"✅ Call session created: {session_id}")
        print(f"   Scenario: {agent_config['scenario_name']}")

        response = {
            "session_id": session_id,
            "scenario": agent_config['scenario_name'],
            "ready": True
        }

        if research_data:
            response["research_data"] = research_data

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up call: {str(e)}")


@app.post("/api/call/start/{session_id}")
async def start_call(session_id: str, phone_data: dict):
    """
    Start phone call to user's number

    Request body:
    {
        "phone_number": "+33612345678"
    }

    Returns:
        {
            "call_id": str (if successful),
            "status": "initiated" | "unavailable",
            "message": str,
            "alternatives": {...} (if unavailable)
        }
    """

    if not phone_call_handler:
        raise HTTPException(
            status_code=503,
            detail="Phone Call Handler not available"
        )

    # Get session
    session = call_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["status"] != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Session not ready (current status: {session['status']})"
        )

    try:
        phone_number = phone_data.get("phone_number")
        if not phone_number:
            raise HTTPException(status_code=400, detail="phone_number is required")

        # Get agent_id from session
        agent_id = session["agent_config"].get("agent_id")

        if not agent_id:
            # If agent creation failed, return error
            error = session["agent_config"].get("error")
            raise HTTPException(
                status_code=503,
                detail=f"Agent not available: {error if error else 'Agent ID missing'}"
            )

        # Attempt to initiate call via Twilio
        call_result = await phone_call_handler.initiate_call(
            phone_number=phone_number,
            agent_id=agent_id
        )

        if call_result["status"] == "initiated":
            # Update session
            session["call_sid"] = call_result["call_sid"]
            session["phone_number"] = phone_number
            session["status"] = "in_progress"

            return {
                "call_sid": call_result["call_sid"],
                "status": "initiated",
                "message": call_result["message"]
            }
        elif call_result["status"] == "unavailable":
            # Twilio not configured
            return {
                "status": "unavailable",
                "message": "Twilio n'est pas configuré. Les appels téléphoniques ne sont pas disponibles.",
                "error": call_result.get("error"),
                "suggestion": "Veuillez configurer Twilio dans le fichier .env (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)"
            }
        else:
            # Error occurred
            return {
                "status": "error",
                "message": call_result.get("message"),
                "error": call_result.get("error")
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting call: {str(e)}")


@app.get("/api/call/twiml/{agent_id}")
@app.post("/api/call/twiml/{agent_id}")
async def get_twiml(agent_id: str):
    """
    TwiML endpoint for Twilio to connect call to ElevenLabs WebSocket

    Twilio calls this when user answers the phone.
    Returns XML instructions to stream audio to/from ElevenLabs.
    """
    from fastapi.responses import Response

    # For test_agent, return simple test message
    if agent_id == "test_agent":
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="fr-FR">Bonjour! Ceci est un test de Twilio. Si vous entendez ce message, votre configuration fonctionne parfaitement. Au revoir!</Say>
</Response>"""
        print(f"📞 Serving test TwiML")
        return Response(content=twiml, media_type="application/xml")

    if not phone_call_handler:
        raise HTTPException(status_code=503, detail="Phone Call Handler not available")

    try:
        # Generate TwiML
        twiml = phone_call_handler.generate_twiml(agent_id)

        print(f"📞 Serving TwiML for agent: {agent_id}")

        # Return XML response
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"❌ TwiML generation error: {e}")
        raise HTTPException(status_code=500, detail=f"TwiML error: {str(e)}")


@app.post("/api/call/status")
async def call_status_callback(
    CallSid: str = None,
    CallStatus: str = None,
    From: str = None,
    To: str = None
):
    """
    Twilio status callback endpoint

    Receives updates about call status (initiated, ringing, answered, completed)
    """

    print(f"📞 Twilio status callback:")
    print(f"   Call SID: {CallSid}")
    print(f"   Status: {CallStatus}")
    print(f"   From: {From}")
    print(f"   To: {To}")

    # Find session by call_sid
    session = next(
        (s for s in call_sessions.values() if s.get("call_sid") == CallSid),
        None
    )

    if session:
        # Update session status
        if CallStatus == "completed":
            session["status"] = "waiting_analysis"
            print(f"   Session updated: waiting for transcript")
        elif CallStatus in ["failed", "busy", "no-answer"]:
            session["status"] = "failed"
            print(f"   Call failed: {CallStatus}")

    return {"status": "received"}


@app.get("/api/call/results/{session_id}")
async def get_call_results(session_id: str):
    """
    Get analysis results for a completed call

    Returns:
        {
            "status": "ready" | "in_progress" | "completed" | "not_found",
            "transcript": str (if completed),
            "duration": int (if completed),
            "recording_url": str (if available),
            "analysis": {...} (if completed)
        }
    """

    session = call_sessions.get(session_id)

    if not session:
        return {"status": "not_found"}

    if session["status"] != "completed":
        return {
            "status": session["status"],
            "message": f"Call is {session['status']}"
        }

    return {
        "status": "completed",
        "transcript": session.get("transcript"),
        "duration": session.get("duration"),
        "recording_url": session.get("recording_url"),
        "analysis": session.get("analysis"),
        "scenario": session["scenario"],
        "context": session["context"]
    }


@app.delete("/api/call/session/{session_id}")
async def delete_call_session(session_id: str):
    """Delete a call session"""

    if session_id in call_sessions:
        del call_sessions[session_id]
        return {"status": "deleted"}

    return {"status": "not_found"}


# ============================================================================
# WEBHOOK ENDPOINTS (ElevenLabs Callbacks)
# ============================================================================

@app.get("/webhook/test")
@app.post("/webhook/test")
async def test_webhook():
    """
    Endpoint de test pour vérifier que le webhook est accessible
    Utilisez ceci pour tester que ngrok fonctionne:
    curl https://your-ngrok-url.ngrok-free.app/webhook/test
    """
    return {
        "status": "ok",
        "message": "Webhook endpoint is accessible!",
        "timestamp": json.dumps({"time": "now"})
    }

@app.post("/api/elevenlabs-webhook")
async def elevenlabs_official_webhook(request: dict):
    """
    Endpoint webhook officiel ElevenLabs
    URL: https://your-ngrok-url.ngrok-free.app/api/elevenlabs-webhook

    ElevenLabs envoie les événements de conversation ici
    """

    print(f"\n{'='*70}")
    print(f"📞 ELEVENLABS WEBHOOK RECEIVED")
    print(f"{'='*70}")
    print(f"📦 Full payload:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print(f"{'='*70}\n")

    try:
        # Extraire les données (ElevenLabs peut envoyer différents formats)
        agent_id = request.get("agent_id") or request.get("agentId")
        conversation_id = request.get("conversation_id") or request.get("conversationId")

        # Le transcript peut être à différents endroits
        transcript = ""
        if "transcript" in request:
            transcript = request["transcript"]
        elif "analysis" in request and "transcript" in request["analysis"]:
            transcript = request["analysis"]["transcript"]
        elif "conversation" in request and "transcript" in request["conversation"]:
            transcript = request["conversation"]["transcript"]

        duration = request.get("duration", 0)
        status = request.get("status", "completed")

        print(f"🔍 Extracted data:")
        print(f"   Agent ID: {agent_id}")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   Transcript length: {len(transcript)} chars")
        print(f"   Duration: {duration}s")

        # Trouver la session correspondante
        session_id = None
        for sid, session in call_sessions.items():
            if session.get("agent_config", {}).get("agent_id") == agent_id:
                session_id = sid
                break

        if not session_id:
            print(f"⚠️ No session found for agent_id: {agent_id}")
            print(f"   Available sessions: {list(call_sessions.keys())}")
            print(f"   Available agent_ids: {[s.get('agent_config', {}).get('agent_id') for s in call_sessions.values()]}")
            return {"status": "no_session_found", "message": "Session not found"}

        session = call_sessions[session_id]

        # Stocker le transcript et les métadonnées
        session["transcript"] = transcript
        session["duration"] = duration
        session["conversation_id"] = conversation_id
        session["call_status"] = status
        session["status"] = "analyzing"

        print(f"📝 Transcript received for session {session_id}")

        # Analyser avec Mistral si disponible et si transcript non vide
        if mistral and transcript and len(transcript) > 10:
            print("🎯 Starting Mistral AI analysis...")

            analysis = await analyze_negotiation_performance(
                transcript=transcript,
                user_context=session["context"],
                mistral_service=mistral
            )

            session["analysis"] = analysis
            session["status"] = "completed"

            print(f"✅ Analysis completed")
            print(f"   Score: {analysis.get('score', 0)}/100")
            print(f"   Outcome: {analysis.get('outcome', 'unknown')}")
        else:
            session["status"] = "completed"
            if not transcript or len(transcript) <= 10:
                print("⚠️ Transcript too short or empty - skipping analysis")
            else:
                print("⚠️ Mistral not available - skipping analysis")

        return {
            "status": "success",
            "message": "Webhook processed",
            "session_id": session_id
        }

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@app.post("/webhook/elevenlabs/call-ended")
async def elevenlabs_call_ended_webhook(data: dict):
    """
    Webhook appelé par ElevenLabs quand une conversation se termine

    ElevenLabs peut envoyer différents formats selon le type d'événement.
    On log tout pour débugger.
    """

    print(f"\n{'='*70}")
    print(f"📞 WEBHOOK RECEIVED: ElevenLabs Call Ended")
    print(f"{'='*70}")
    print(f"📦 Full payload received:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"{'='*70}\n")

    try:
        # ElevenLabs peut envoyer différents formats
        # Essayer plusieurs clés possibles
        call_id = data.get("call_id") or data.get("conversation_id")
        agent_id = data.get("agent_id") or data.get("agentId")

        # Le transcript peut être dans différents endroits
        transcript = ""
        if "transcript" in data:
            transcript = data["transcript"]
        elif "analysis" in data and "transcript" in data["analysis"]:
            transcript = data["analysis"]["transcript"]
        elif "metadata" in data and "transcript" in data["metadata"]:
            transcript = data["metadata"]["transcript"]

        duration = data.get("duration", 0)
        status = data.get("status", "unknown")

        print(f"🔍 Extracted data:")
        print(f"   Agent ID: {agent_id}")
        print(f"   Call ID: {call_id}")
        print(f"   Transcript length: {len(transcript)} chars")
        print(f"   Duration: {duration}s")

        # Find session by agent_id
        session_id = None
        for sid, session in call_sessions.items():
            if session.get("agent_config", {}).get("agent_id") == agent_id:
                session_id = sid
                break

        if not session_id:
            print(f"⚠️ No session found for agent_id: {agent_id}")
            print(f"   Available sessions: {list(call_sessions.keys())}")
            print(f"   Available agent_ids: {[s.get('agent_config', {}).get('agent_id') for s in call_sessions.values()]}")
            return {"status": "no_session_found", "message": "Session not found for this agent"}

        session = call_sessions[session_id]

        # Store transcript and metadata
        session["transcript"] = transcript
        session["duration"] = duration
        session["call_id"] = call_id
        session["call_status"] = status
        session["status"] = "analyzing"

        print(f"📝 Transcript received ({len(transcript)} chars)")

        # Analyze performance with Mistral
        if mistral and transcript:
            print("🎯 Starting negotiation performance analysis...")
            analysis = await analyze_negotiation_performance(
                transcript=transcript,
                user_context=session["context"],
                mistral_service=mistral
            )

            session["analysis"] = analysis
            session["status"] = "completed"

            print(f"✅ Analysis completed")
            print(f"   Score: {analysis.get('score')}/100")
            print(f"   Outcome: {analysis.get('outcome')}")
        else:
            session["status"] = "completed"
            print("⚠️ No Mistral service available - skipping analysis")

        return {
            "status": "success",
            "message": "Call data processed and analyzed",
            "session_id": session_id
        }

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@app.get("/api/call/analysis/{session_id}")
async def get_call_analysis(session_id: str):
    """
    Récupérer l'analyse et le score d'une négociation

    Returns:
        {
            "status": "analyzing" | "completed",
            "transcript": str,
            "duration": int,
            "analysis": {
                "score": int,
                "outcome": str,
                "strengths": List[str],
                "weaknesses": List[str],
                "tactics_used": List[str],
                "price_negotiated": str | null,
                "recommendations": List[str]
            }
        }
    """

    session = call_sessions.get(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["status"] not in ["analyzing", "completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Call not yet completed. Status: {session['status']}"
        )

    return {
        "status": session["status"],
        "transcript": session.get("transcript"),
        "duration": session.get("duration"),
        "call_status": session.get("call_status"),
        "analysis": session.get("analysis"),
        "context": session["context"],
        "research_data": session.get("research_data")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

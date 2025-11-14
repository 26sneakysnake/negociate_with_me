# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import get_settings
from models import (
    NegotiationContext, Strategy, TranscriptAnalysis, Analysis, Session
)
from services.mistral_service import MistralService
from services.qdrant_service import QdrantService
from services.elevenlabs_service import ElevenLabsService
from typing import Dict
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

# Mount static files for audio
os.makedirs("audio_files", exist_ok=True)
app.mount("/audio", StaticFiles(directory="audio_files"), name="audio")

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

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize services and database"""
    print("\n" + "="*70)
    print("🚀 Starting NegotiAI v0 Backend")
    print("="*70)

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
async def generate_strategy(context: NegotiationContext):
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

        # Store session
        session = Session(
            id=strategy.session_id,
            context=context,
            strategy=strategy
        )
        sessions[strategy.session_id] = session

        return strategy

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating strategy: {str(e)}")

@app.post("/api/analyze-negotiation", response_model=Analysis)
async def analyze_negotiation(analysis_input: TranscriptAnalysis):
    """Analyze negotiation transcript"""
    # Check if required services are available
    if mistral is None:
        raise HTTPException(
            status_code=503,
            detail="Mistral AI service not available. Please check API key configuration."
        )

    try:
        # Get session
        session = sessions.get(analysis_input.session_id)
        if not session or not session.strategy:
            raise HTTPException(status_code=404, detail="Session or strategy not found")

        # Embed transcript to find relevant tactics
        relevant_tactics = []
        if qdrant is not None:
            try:
                transcript_embedding = mistral.embed_text(analysis_input.transcript[:1000])
                relevant_tactics = await qdrant.search_relevant_tactics(
                    transcript_embedding,
                    limit=15
                )
            except Exception as e:
                print(f"⚠️ Could not retrieve tactics from Qdrant: {e}")
                # Continue without tactics

        # Analyze performance
        analysis = await mistral.analyze_negotiation(
            strategy=session.strategy,
            transcript=analysis_input.transcript,
            actual_outcome=analysis_input.actual_outcome,
            tactics_context=relevant_tactics
        )

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

        # Update session
        session.analysis = analysis

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

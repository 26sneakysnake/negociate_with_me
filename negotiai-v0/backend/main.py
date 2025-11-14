# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import get_settings
from backend.models import (
    NegotiationContext, Strategy, TranscriptAnalysis, Analysis, Session
)
from backend.services.mistral_service import MistralService
from backend.services.qdrant_service import QdrantService
from backend.services.elevenlabs_service import ElevenLabsService
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

# Services
mistral = MistralService()
qdrant = QdrantService()
elevenlabs = ElevenLabsService()

# In-memory session storage (use Redis in production)
sessions: Dict[str, Session] = {}

# Startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load tactics"""
    await qdrant.initialize_collection()
    # Load tactics if collection is empty
    try:
        count = await qdrant.load_tactics_database("backend/data/negotiation_tactics.json")
        print(f"✅ Loaded {count} negotiation tactics into Qdrant")
    except Exception as e:
        print(f"⚠️ Could not load tactics: {e}")

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
    try:
        # Embed the context to find relevant tactics
        context_embedding = mistral.embed_text(
            f"{context.objective} {context.context_text[:500]}"
        )

        # Search for relevant tactics
        relevant_tactics = await qdrant.search_relevant_tactics(
            context_embedding,
            limit=10
        )

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
    try:
        # Get session
        session = sessions.get(analysis_input.session_id)
        if not session or not session.strategy:
            raise HTTPException(status_code=404, detail="Session or strategy not found")

        # Embed transcript to find relevant tactics
        transcript_embedding = mistral.embed_text(analysis_input.transcript[:1000])
        relevant_tactics = await qdrant.search_relevant_tactics(
            transcript_embedding,
            limit=15
        )

        # Analyze performance
        analysis = await mistral.analyze_negotiation(
            strategy=session.strategy,
            transcript=analysis_input.transcript,
            actual_outcome=analysis_input.actual_outcome,
            tactics_context=relevant_tactics
        )

        # Generate audio feedback
        feedback_text = elevenlabs.format_analysis_for_speech(analysis)
        audio_file = await elevenlabs.generate_feedback_audio(
            feedback_text,
            f"{analysis_input.session_id}.mp3"
        )
        analysis.audio_url = f"/audio/{analysis_input.session_id}.mp3"

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

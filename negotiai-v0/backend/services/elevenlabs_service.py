# backend/services/elevenlabs_service.py
from elevenlabs.client import ElevenLabs
from config import get_settings
import os
import uuid

class ElevenLabsService:
    def __init__(self):
        settings = get_settings()
        self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        # Using a professional voice
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

    async def generate_feedback_audio(
        self,
        analysis_text: str,
        output_path: str = None
    ) -> str:
        """Generate audio feedback from analysis"""

        # Format analysis into natural speech
        script = f"""
        Here's your negotiation performance feedback.

        {analysis_text}

        Keep practicing these techniques, and you'll continue to improve!
        """

        # Generate audio using the new API
        audio_generator = self.client.text_to_speech.convert(
            text=script,
            voice_id=self.voice_id,
            model_id="eleven_monolingual_v1"
        )

        # Save audio file
        if output_path is None:
            output_path = f"feedback_{uuid.uuid4()}.mp3"

        os.makedirs("audio_files", exist_ok=True)
        file_path = f"audio_files/{output_path}"

        with open(file_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)

        return file_path

    def format_analysis_for_speech(self, analysis) -> str:
        """Convert analysis object to natural speech text"""
        text = f"""
        Overall performance: {analysis.performance.overall_score} out of 100.

        Your strengths included: {', '.join(analysis.strengths)}.

        Areas to improve: {', '.join(analysis.weaknesses)}.

        Key recommendations: {'. '.join(analysis.key_recommendations)}.
        """
        return text

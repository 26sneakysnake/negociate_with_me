"""
WebSocket Handler for Real-Time Voice Simulation
Manages bidirectional audio streaming and real-time analysis
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import json
import uuid
import asyncio
import base64
from datetime import datetime

from audio.elevenlabs_client import ElevenLabsVoiceAgent
from ai.realtime_analyzer import RealtimeAnalyzer


# Active simulation sessions
sessions: Dict[str, dict] = {}


class SimulationSession:
    """Manages a single voice simulation session"""

    def __init__(
        self,
        session_id: str,
        websocket: WebSocket,
        context: Dict,
        elevenlabs_agent: ElevenLabsVoiceAgent,
        realtime_analyzer: RealtimeAnalyzer
    ):
        self.session_id = session_id
        self.websocket = websocket
        self.context = context
        self.elevenlabs = elevenlabs_agent
        self.analyzer = realtime_analyzer

        # Session state
        self.is_active = False
        self.auto_pilot_enabled = False
        self.opponent_agent_id = None
        self.conversation_history = []
        self.current_turn = 0

        # Opponent's scripted responses (for MVP demo)
        self.opponent_script = context.get("opponent_script", [
            "Bonjour, votre solution m'intéresse mais le prix me semble élevé.",
            "Vos concurrents proposent des prix 30% moins chers.",
            "J'ai besoin d'une décision aujourd'hui, mon budget est limité.",
            "C'est vraiment mon maximum, je ne peux pas aller plus haut."
        ])
        self.script_index = 0

    async def start(self):
        """Start the simulation session"""

        self.is_active = True

        # Create opponent agent
        opponent_config = await self.elevenlabs.create_opponent_agent(self.context)
        self.opponent_agent_id = opponent_config["agent_id"]

        # Send welcome message
        await self.send_message({
            "type": "status",
            "message": "✅ Simulation ready! Opponent agent created.",
            "agent_id": self.opponent_agent_id
        })

        # Send first opponent message
        await self._opponent_speaks()

    async def handle_message(self, data: dict):
        """Handle incoming message from client"""

        msg_type = data.get("type")

        if msg_type == "audio":
            # User audio chunk received
            await self._handle_user_audio(data)

        elif msg_type == "transcript":
            # User provided manual transcript (for testing)
            await self._handle_user_transcript(data)

        elif msg_type == "autopilot_toggle":
            # Toggle auto-pilot mode
            self.auto_pilot_enabled = data.get("enabled", False)
            await self.send_message({
                "type": "autopilot_status",
                "enabled": self.auto_pilot_enabled
            })

        elif msg_type == "autopilot_activate":
            # Activate auto-pilot for current situation
            await self._activate_autopilot(data)

        elif msg_type == "stop":
            # Stop simulation
            await self.stop()

    async def _handle_user_audio(self, data: dict):
        """Process user audio input"""

        # Get audio bytes
        audio_base64 = data.get("audio")
        audio_bytes = base64.b64decode(audio_base64)

        # Transcribe (placeholder - integrate Whisper)
        transcript = "[Transcription en cours...]"
        # In production: transcript = await self.elevenlabs.transcribe_audio(audio_bytes)

        # For MVP, use provided text if available
        if data.get("text"):
            transcript = data["text"]

        await self._handle_user_transcript({"text": transcript})

    async def _handle_user_transcript(self, data: dict):
        """Process user transcript and generate analysis"""

        user_text = data.get("text", "")

        if not user_text.strip():
            return

        # Add to conversation history
        self.conversation_history.append({
            "turn": self.current_turn,
            "speaker": "user",
            "text": user_text,
            "timestamp": datetime.now().isoformat()
        })

        # Send transcript to frontend
        await self.send_message({
            "type": "transcript",
            "speaker": "user",
            "text": user_text,
            "turn": self.current_turn
        })

        # Analyze user's response
        analysis = await self.analyzer.analyze_turn(
            transcript=user_text,
            speaker="user",
            context=self.context,
            conversation_history=self.conversation_history
        )

        # Send suggestion if available
        if analysis.get("suggestion"):
            await self.send_message({
                "type": "suggestion",
                **analysis
            })

        self.current_turn += 1

        # Opponent responds
        await asyncio.sleep(1)  # Natural pause
        await self._opponent_speaks()

    async def _opponent_speaks(self):
        """Generate and send opponent response"""

        # For MVP, use scripted responses
        if self.script_index < len(self.opponent_script):
            opponent_text = self.opponent_script[self.script_index]
            self.script_index += 1
        else:
            # End of script
            opponent_text = "Merci pour cette discussion. Je vais réfléchir à votre proposition."
            await self.send_message({
                "type": "status",
                "message": "🏁 Simulation terminée"
            })

        # Add to history
        self.conversation_history.append({
            "turn": self.current_turn,
            "speaker": "opponent",
            "text": opponent_text,
            "timestamp": datetime.now().isoformat()
        })

        # Send transcript
        await self.send_message({
            "type": "transcript",
            "speaker": "opponent",
            "text": opponent_text,
            "turn": self.current_turn
        })

        # Generate audio
        opponent_audio = await self.elevenlabs.generate_opponent_response(opponent_text)

        if opponent_audio:
            # Send audio to frontend
            audio_base64 = base64.b64encode(opponent_audio).decode('utf-8')
            await self.send_message({
                "type": "opponent_audio",
                "audio": audio_base64,
                "format": "mp3"
            })

        # Analyze opponent's statement and generate suggestion
        analysis = await self.analyzer.analyze_turn(
            transcript=opponent_text,
            speaker="opponent",
            context=self.context,
            conversation_history=self.conversation_history
        )

        if analysis.get("suggestion"):
            await self.send_message({
                "type": "suggestion",
                **analysis
            })

        self.current_turn += 1

    async def _activate_autopilot(self, data: dict):
        """Activate auto-pilot mode with AI response"""

        # Get last suggestion's tactic
        tactic = data.get("tactic")

        if not tactic:
            await self.send_message({
                "type": "error",
                "message": "Aucune tactique disponible pour auto-pilot"
            })
            return

        # Generate auto-pilot response
        autopilot_audio = await self.elevenlabs.generate_autopilot_response(
            tactic=tactic,
            context=self.context,
            voice_id=self.elevenlabs.cloned_voice_id
        )

        if not autopilot_audio:
            await self.send_message({
                "type": "error",
                "message": "Erreur génération auto-pilot"
            })
            return

        # Extract text from tactic for display
        tactic_texts = {
            "counter_lowball": f"Je comprends votre comparaison, mais regardons le ROI réel sur {self.context.get('timeframe', '12 mois')}.",
            "expose_urgency": "Puis-je vous demander : qu'est-ce qui motive cette deadline précisément ?",
            "firm_boundary": f"Notre prix minimum est {self.context.get('minimum_price', 'X€')}. En dessous, nous ne pouvons garantir la qualité.",
            "value_justification": f"Voici pourquoi notre prix est justifié : {', '.join(self.context.get('value_props', ['qualité', 'support']))}.",
            "confident_close": f"Basé sur notre discussion, je propose {self.context.get('proposed_price', self.context.get('target_price'))}. On avance ?",
            "deflect_objection": "C'est une bonne question. Voici comment on gère ça..."
        }

        autopilot_text = tactic_texts.get(tactic, "Réponse auto-pilot...")

        # Add to conversation history
        self.conversation_history.append({
            "turn": self.current_turn,
            "speaker": "user_autopilot",
            "text": autopilot_text,
            "tactic": tactic,
            "timestamp": datetime.now().isoformat()
        })

        # Send autopilot transcript
        await self.send_message({
            "type": "transcript",
            "speaker": "user_autopilot",
            "text": autopilot_text,
            "turn": self.current_turn,
            "tactic": tactic
        })

        # Send autopilot audio
        audio_base64 = base64.b64encode(autopilot_audio).decode('utf-8')
        await self.send_message({
            "type": "autopilot_audio",
            "audio": audio_base64,
            "format": "mp3",
            "tactic": tactic
        })

        self.current_turn += 1

        # Opponent responds to autopilot
        await asyncio.sleep(2)
        await self._opponent_speaks()

    async def send_message(self, data: dict):
        """Send message to client via WebSocket"""
        try:
            await self.websocket.send_json(data)
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    async def stop(self):
        """Stop the simulation session"""

        self.is_active = False

        # Get conversation summary
        summary = self.analyzer.get_conversation_summary()

        await self.send_message({
            "type": "summary",
            "data": summary,
            "conversation_history": self.conversation_history
        })

        # Reset analyzer
        self.analyzer.reset()


async def handle_simulation_websocket(
    websocket: WebSocket,
    elevenlabs_agent: ElevenLabsVoiceAgent,
    realtime_analyzer: RealtimeAnalyzer,
    context: Dict
):
    """
    Main WebSocket handler for voice simulation

    Args:
        websocket: WebSocket connection
        elevenlabs_agent: ElevenLabs client instance
        realtime_analyzer: Realtime analyzer instance
        context: Negotiation context from client
    """

    await websocket.accept()
    session_id = str(uuid.uuid4())

    print(f"🔌 New simulation session: {session_id}")

    # Create session
    session = SimulationSession(
        session_id=session_id,
        websocket=websocket,
        context=context,
        elevenlabs_agent=elevenlabs_agent,
        realtime_analyzer=realtime_analyzer
    )

    sessions[session_id] = session

    try:
        # Start simulation
        await session.start()

        # Handle incoming messages
        while session.is_active:
            try:
                # Wait for message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=300  # 5 min timeout
                )

                await session.handle_message(data)

            except asyncio.TimeoutError:
                print(f"⏰ Session {session_id} timeout")
                break

    except WebSocketDisconnect:
        print(f"👋 Client disconnected: {session_id}")

    except Exception as e:
        print(f"❌ Session error: {e}")
        await session.send_message({
            "type": "error",
            "message": str(e)
        })

    finally:
        # Cleanup
        if session_id in sessions:
            del sessions[session_id]
        print(f"🧹 Session cleaned up: {session_id}")

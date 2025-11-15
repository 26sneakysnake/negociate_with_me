"""
ElevenLabs Voice Agent for NegotiAI
Handles conversational AI opponent and voice cloning for auto-pilot
"""

from elevenlabs.client import ElevenLabs
import os
import json
import asyncio
from typing import Dict, Optional
import httpx


class ElevenLabsVoiceAgent:
    """Manages ElevenLabs conversational AI and voice cloning"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = ElevenLabs(api_key=api_key)
        self.base_url = "https://api.elevenlabs.io/v1"

        # Voice IDs
        self.opponent_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional female
        self.cloned_voice_id = None

    async def create_opponent_agent(self, scenario: dict) -> dict:
        """
        Create a conversational AI agent that plays a difficult client

        Args:
            scenario: {
                "context": str,
                "target_price": str,
                "opponent_goal": str,
                "tactics": ["lowball", "urgency", "aggressive"]
            }

        Returns:
            {
                "agent_id": str,
                "conversation_id": str,
                "voice_id": str
            }
        """

        # Build opponent persona with negotiation tactics
        system_prompt = f"""You are a tough but professional client negotiating a business deal.

CONTEXT:
{scenario.get('context', 'Business negotiation')}

YOUR GOAL:
- Get the best price possible (target: {scenario.get('opponent_goal', 'lowest price')})
- Push back on high prices
- Use professional negotiation tactics

TACTICS TO USE:
1. LOWBALL: "That's too expensive, competitors offer similar for 40% less"
2. FALSE URGENCY: "I need a decision today, other vendors are waiting"
3. OBJECTIONS: Point out missing features or concerns
4. BUDGET CONSTRAINT: "My maximum budget is X, can't go higher"

STYLE:
- Professional but firm
- Don't accept first offer
- Show skepticism about value
- Ask challenging questions
- Eventually negotiate if good arguments presented

IMPORTANT:
- Speak naturally in French
- Keep responses under 30 seconds
- Be realistic (don't be impossible, just difficult)
- If user provides strong value proposition, show interest
"""

        # For MVP, return mock agent configuration
        # In production, this would call ElevenLabs Conversational AI API
        return {
            "agent_id": f"opponent_{hash(system_prompt) % 10000}",
            "system_prompt": system_prompt,
            "voice_id": self.opponent_voice_id,
            "conversation_id": None  # Will be set when conversation starts
        }

    async def clone_user_voice(self, audio_sample: bytes, name: str = "user_voice") -> str:
        """
        Clone user's voice for auto-pilot mode

        Args:
            audio_sample: Audio bytes (at least 1 minute of clear speech)
            name: Name for the cloned voice

        Returns:
            voice_id: ID of cloned voice
        """

        try:
            # Create voice from sample
            async with httpx.AsyncClient() as client:
                files = {
                    'files': ('sample.mp3', audio_sample, 'audio/mpeg')
                }
                data = {
                    'name': name,
                    'description': 'User voice clone for auto-pilot negotiation'
                }

                response = await client.post(
                    f"{self.base_url}/voices/add",
                    headers={"xi-api-key": self.api_key},
                    files=files,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    self.cloned_voice_id = result['voice_id']
                    print(f"✅ Voice cloned successfully: {self.cloned_voice_id}")
                    return self.cloned_voice_id
                else:
                    print(f"❌ Voice cloning failed: {response.text}")
                    # Fallback to default voice
                    return self.opponent_voice_id

        except Exception as e:
            print(f"⚠️ Voice cloning error: {e}")
            # Use default voice as fallback
            return self.opponent_voice_id

    async def generate_autopilot_response(
        self,
        tactic: str,
        context: dict,
        voice_id: Optional[str] = None
    ) -> bytes:
        """
        Generate tactical response audio with cloned voice for auto-pilot

        Args:
            tactic: Tactic to apply (e.g., "counter_lowball", "expose_urgency")
            context: Current negotiation context
            voice_id: Voice to use (defaults to cloned voice or fallback)

        Returns:
            audio_bytes: MP3 audio data
        """

        # Tactical response templates
        TACTIC_RESPONSES = {
            "counter_lowball": {
                "template": "Je comprends votre comparaison avec {competitor}, mais regardons le ROI réel. Avec notre solution, vous économisez {value} en {timeframe}. Si on compare la valeur totale plutôt que juste le prix, on est largement compétitifs.",
                "tone": "confident, analytical"
            },
            "expose_urgency": {
                "template": "J'apprécie votre intérêt. Puis-je vous demander : qu'est-ce qui motive cette deadline aujourd'hui ? Souvent, prendre une semaine de plus pour bien évaluer permet d'éviter des regrets. Quelle est la vraie contrainte ?",
                "tone": "calm, curious"
            },
            "firm_boundary": {
                "template": "Je vous ai présenté notre meilleure offre à {price}. En dessous de {minimum}, nous ne pouvons pas garantir la qualité de service que vous attendez. Qu'est-ce qui vous permettrait d'accepter à ce niveau ?",
                "tone": "firm, professional"
            },
            "value_justification": {
                "template": "Voici pourquoi notre prix est justifié : {value_prop_1}, {value_prop_2}, et {value_prop_3}. Aucun concurrent n'offre cette combinaison. C'est ça la différence de valeur.",
                "tone": "assertive, evidence-based"
            },
            "confident_close": {
                "template": "Basé sur ce qu'on a discuté, je pense qu'on a une solution qui répond à vos besoins. Si on signe à {proposed_price}, je peux vous garantir {extra_benefit}. On avance ?",
                "tone": "confident, decisive"
            },
            "deflect_objection": {
                "template": "C'est une bonne question sur {objection}. Voici comment on gère ça : {counter_argument}. Est-ce que ça répond à votre préoccupation ?",
                "tone": "helpful, solution-oriented"
            }
        }

        # Get tactic template
        tactic_data = TACTIC_RESPONSES.get(tactic, TACTIC_RESPONSES["value_justification"])

        # Fill template with context
        text = tactic_data["template"].format(
            competitor=context.get("competitor", "la concurrence"),
            value=context.get("value_proposition", "X€"),
            timeframe=context.get("timeframe", "6 mois"),
            price=context.get("target_price", ""),
            minimum=context.get("minimum_price", ""),
            value_prop_1=context.get("value_props", ["qualité", "support", "ROI"])[0],
            value_prop_2=context.get("value_props", ["qualité", "support", "ROI"])[1] if len(context.get("value_props", [])) > 1 else "support premium",
            value_prop_3=context.get("value_props", ["qualité", "support", "ROI"])[2] if len(context.get("value_props", [])) > 2 else "résultats garantis",
            proposed_price=context.get("proposed_price", context.get("target_price", "")),
            extra_benefit=context.get("extra_benefit", "un support premium"),
            objection=context.get("last_objection", "ce point"),
            counter_argument=context.get("counter_argument", "notre approche unique")
        )

        # Use cloned voice or fallback
        use_voice = voice_id or self.cloned_voice_id or self.opponent_voice_id

        # Generate speech
        try:
            audio = self.client.generate(
                text=text,
                voice=use_voice,
                model="eleven_multilingual_v2"
            )

            # Convert generator to bytes
            audio_bytes = b"".join(audio)

            print(f"✅ Generated auto-pilot response ({len(audio_bytes)} bytes)")
            print(f"   Tactic: {tactic}")
            print(f"   Text: {text[:100]}...")

            return audio_bytes

        except Exception as e:
            print(f"❌ Error generating auto-pilot audio: {e}")
            return b""

    async def generate_opponent_response(self, text: str, voice_id: Optional[str] = None) -> bytes:
        """
        Generate opponent's response audio

        Args:
            text: What the opponent says
            voice_id: Voice to use (defaults to opponent voice)

        Returns:
            audio_bytes: MP3 audio data
        """

        use_voice = voice_id or self.opponent_voice_id

        try:
            audio = self.client.generate(
                text=text,
                voice=use_voice,
                model="eleven_multilingual_v2"
            )

            audio_bytes = b"".join(audio)
            print(f"🎤 Opponent says: {text[:80]}...")

            return audio_bytes

        except Exception as e:
            print(f"❌ Error generating opponent audio: {e}")
            return b""

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio to text (using ElevenLabs or external service)

        For MVP, you might want to use Whisper API or similar
        This is a placeholder implementation
        """
        # TODO: Implement with Whisper or ElevenLabs transcription
        # For now, return placeholder
        return "[Transcription placeholder - integrate Whisper API]"

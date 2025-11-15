"""
ElevenLabs Conversational AI Agent Service
Manages real-time voice conversations with intelligent AI opponent
"""

import asyncio
import json
import uuid
from typing import Dict, Optional
import httpx


class ElevenLabsConversationalAgent:
    """
    Manages ElevenLabs Conversational AI for voice negotiation training

    This uses ElevenLabs' Conversational AI API which provides:
    - Speech-to-Text (user speaks)
    - AI conversation logic
    - Text-to-Speech (agent responds)
    All in real-time via WebSocket
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.agent_id = None

    async def create_negotiation_agent(
        self,
        context: Dict,
        research_data: Dict = None
    ) -> Dict:
        """
        Create a conversational AI agent configured as a negotiation opponent

        Args:
            context: Negotiation context (product, target price, etc.)
            research_data: Enriched data from web research

        Returns:
            {
                "agent_id": str,
                "conversation_id": str,
                "websocket_url": str
            }
        """

        # Build agent persona based on context and research
        product_info = research_data.get("product", {}) if research_data else {}
        client_info = research_data.get("client", {}) if research_data else {}

        # Create agent system prompt with enriched context
        system_prompt = self._build_agent_prompt(context, product_info, client_info)

        # Agent configuration
        agent_config = {
            "name": f"Negotiation Opponent - {context.get('product', 'Client')}",
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice (professional)
            "language": "fr",  # French
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt
                    },
                    "first_message": self._get_opening_message(context, client_info)
                },
                "tts": {
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            }
        }

        print(f"🎙️ Creating ElevenLabs Conversational Agent...")
        print(f"   Product: {context.get('product')}")
        print(f"   Target Price: {context.get('target_price')}")

        try:
            async with httpx.AsyncClient() as client:
                # Create conversational agent
                response = await client.post(
                    f"{self.base_url}/convai/agents",
                    headers={
                        "xi-api-key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=agent_config,
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    result = response.json()
                    self.agent_id = result.get("agent_id")

                    print(f"✅ Agent created: {self.agent_id}")

                    # Get conversation connection details
                    conversation_id = str(uuid.uuid4())

                    return {
                        "agent_id": self.agent_id,
                        "conversation_id": conversation_id,
                        "websocket_url": f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}",
                        "config": agent_config
                    }
                else:
                    print(f"❌ Failed to create agent: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return self._get_fallback_config(context)

        except Exception as e:
            print(f"⚠️ Error creating conversational agent: {e}")
            return self._get_fallback_config(context)

    def _build_agent_prompt(
        self,
        context: Dict,
        product_info: Dict,
        client_info: Dict
    ) -> str:
        """Build system prompt for the agent with all context"""

        competitors = product_info.get("competitors", ["Concurrent A", "Concurrent B"])
        competitor_list = ", ".join(competitors)

        prompt = f"""Tu es un client professionnel qui négocie l'achat de "{context.get('product', 'cette solution')}".

CONTEXTE DE LA NÉGOCIATION:
- Produit proposé: {context.get('product')}
- Prix demandé par le vendeur: {context.get('target_price')}
- Concurrents connus: {competitor_list}
- Ton objectif: {context.get('opponent_goal', 'Obtenir le meilleur prix possible')}

"""

        # Add product context if available
        if product_info.get("typical_pricing"):
            prompt += f"- Prix marché typique: {product_info['typical_pricing']}\n"

        # Add client context if available
        if client_info:
            prompt += f"\nTON PROFIL CLIENT:\n"
            prompt += f"- Taille entreprise: {client_info.get('company_size', 'PME')}\n"
            prompt += f"- Budget type: {client_info.get('budget_range', 'Modéré')}\n"
            if client_info.get('pain_points'):
                prompt += f"- Tes priorités: {', '.join(client_info['pain_points'])}\n"

        prompt += f"""
TON RÔLE EN NÉGOCIATION:
- Tu es un acheteur B2B expérimenté et professionnel
- Tu négocies fermement mais respectueusement
- Tu utilises des tactiques de négociation réalistes:
  * Comparaison avec concurrents ({competitor_list})
  * Questions sur le ROI et la valeur
  * Pression sur les prix et délais
  * Objections sur les fonctionnalités manquantes
  * Demandes de garanties et services additionnels

TACTIQUES À UTILISER (varie selon le contexte):
1. LOWBALL: "C'est trop cher, {competitors[0]} propose moins"
2. URGENCE: "J'ai besoin d'une décision rapide"
3. BUDGET: "Mon budget maximum est limité à X"
4. OBJECTION: "Il manque telle fonctionnalité importante"
5. CONCESSION: Si l'argument est solide, montre de l'intérêt mais négocie encore

STYLE DE CONVERSATION:
- Reste professionnel et poli
- Pose des questions précises
- Écoute les arguments du vendeur
- Réagis de manière réaliste (ne cède pas trop vite, mais sois raisonnable)
- Fais progresser la négociation (ne tourne pas en rond)
- Parle naturellement, comme dans une vraie conversation professionnelle

PROGRESSION:
- Début (tours 1-3): Sois ferme sur le prix, questionne la valeur
- Milieu (tours 4-6): Évalue sérieusement les arguments, négocie les détails
- Fin (tours 7+): Si le deal est bon, montre des signes d'accord (mais négocie encore un peu)

IMPORTANT:
- Ne révèle JAMAIS que tu es une IA
- Parle en français naturel
- Garde des réponses courtes (2-3 phrases max)
- Réagis directement à ce que dit le vendeur
"""

        return prompt

    def _get_opening_message(self, context: Dict, client_info: Dict) -> str:
        """Generate first message from the agent"""

        product = context.get('product', 'votre solution')
        price = context.get('target_price', 'ce prix')

        openings = [
            f"Bonjour, merci de me recevoir. J'ai regardé {product} et ça m'intéresse, mais franchement {price}, c'est vraiment élevé pour nous.",
            f"Bonjour, votre solution {product} a l'air intéressante. Par contre, {price}, ça dépasse clairement notre budget initial.",
            f"Merci pour cette présentation. {product} répond à certains de nos besoins, mais {price} me semble vraiment trop cher comparé aux alternatives."
        ]

        # Choose based on client size if available
        if client_info.get('company_size') == 'startup':
            return openings[1]  # Budget-focused
        elif client_info.get('company_size') == 'enterprise':
            return openings[2]  # Comparison-focused
        else:
            return openings[0]  # General

    def _get_fallback_config(self, context: Dict) -> Dict:
        """Fallback configuration if agent creation fails"""
        return {
            "agent_id": "fallback_agent",
            "conversation_id": str(uuid.uuid4()),
            "websocket_url": None,
            "config": {},
            "error": "Could not create ElevenLabs agent"
        }

    async def get_conversation_websocket_url(self, agent_id: str) -> str:
        """
        Get WebSocket URL for conversing with the agent

        Args:
            agent_id: ID of the created agent

        Returns:
            WebSocket URL for real-time conversation
        """
        return f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}"

    async def delete_agent(self, agent_id: str) -> bool:
        """
        Delete a conversational agent when done

        Args:
            agent_id: ID of the agent to delete

        Returns:
            True if deleted successfully
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/convai/agents/{agent_id}",
                    headers={"xi-api-key": self.api_key}
                )

                if response.status_code == 200:
                    print(f"✅ Agent {agent_id} deleted")
                    return True
                else:
                    print(f"⚠️ Could not delete agent: {response.status_code}")
                    return False

        except Exception as e:
            print(f"⚠️ Error deleting agent: {e}")
            return False

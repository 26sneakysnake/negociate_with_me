"""
Real-time Negotiation Analyzer
Uses Mistral AI + Qdrant for instant tactical suggestions during conversation
"""

from mistralai import Mistral
from qdrant_client import QdrantClient
from typing import Dict, List, Optional
import json
from audio.pattern_detector import PatternDetector


class RealtimeAnalyzer:
    """Analyzes conversation in real-time and generates tactical suggestions"""

    def __init__(self, mistral_key: str, qdrant_url: str, qdrant_key: str):
        self.mistral = Mistral(api_key=mistral_key)
        self.qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_key) if qdrant_url else None
        self.pattern_detector = PatternDetector()

        self.collection_name = "negotiation_tactics"

    async def analyze_turn(
        self,
        transcript: str,
        speaker: str,
        context: dict,
        conversation_history: List[Dict] = None
    ) -> dict:
        """
        Analyze a conversation turn and generate instant suggestion

        Args:
            transcript: What was just said
            speaker: "opponent" or "user"
            context: Negotiation context (product, prices, value props)
            conversation_history: Recent conversation turns

        Returns:
            {
                "suggestion": str,  # Tactical suggestion to display
                "type": "counter"|"warning"|"opportunity",
                "priority": "critical"|"high"|"medium",
                "autopilot_available": bool,
                "tactic": str,  # Tactic name for auto-pilot
                "reasoning": str  # Why this suggestion
            }
        """

        # Step 1: Detect patterns
        patterns = self.pattern_detector.detect(transcript, speaker)

        if not patterns:
            # No critical pattern, generate general suggestion
            return await self._generate_general_suggestion(
                transcript, speaker, context, conversation_history
            )

        # Step 2: Get top priority pattern
        top_pattern = patterns[0]

        # Step 3: Query Qdrant for similar situations (if available)
        similar_tactics = await self._query_similar_tactics(
            transcript,
            top_pattern["pattern"]
        )

        # Step 4: Generate contextual suggestion with Mistral
        suggestion_data = await self._generate_tactical_suggestion(
            transcript=transcript,
            pattern=top_pattern,
            context=context,
            similar_tactics=similar_tactics,
            history=conversation_history
        )

        return suggestion_data

    async def _query_similar_tactics(
        self,
        query_text: str,
        pattern_type: str
    ) -> List[Dict]:
        """Query Qdrant for similar negotiation situations"""

        if not self.qdrant:
            return []

        try:
            # Generate embedding for query
            embedding_response = self.mistral.embeddings.create(
                model="mistral-embed",
                inputs=[query_text]
            )

            query_vector = embedding_response.data[0].embedding

            # Search Qdrant
            search_results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=3,
                query_filter={
                    "must": [
                        {
                            "key": "pattern_type",
                            "match": {"value": pattern_type}
                        }
                    ]
                }
            )

            tactics = []
            for result in search_results:
                tactics.append({
                    "name": result.payload.get("name"),
                    "description": result.payload.get("description"),
                    "example_counter": result.payload.get("example_counter"),
                    "score": result.score
                })

            return tactics

        except Exception as e:
            print(f"⚠️ Qdrant query failed: {e}")
            return []

    async def _generate_tactical_suggestion(
        self,
        transcript: str,
        pattern: Dict,
        context: Dict,
        similar_tactics: List[Dict],
        history: Optional[List[Dict]]
    ) -> Dict:
        """Use Mistral to generate contextual tactical suggestion"""

        # Build context for Mistral
        tactics_context = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in similar_tactics[:2]
        ]) if similar_tactics else "Pas de tactiques similaires"

        history_context = "\n".join([
            f"{h.get('speaker', 'unknown')}: {h.get('text', '')[:100]}"
            for h in (history[-3:] if history else [])
        ])

        # Mistral prompt for tactical suggestion
        prompt = f"""Tu es un expert en négociation. Analyse la situation et donne UNE suggestion tactique ultra-précise.

CONTEXTE NÉGOCIATION:
Produit: {context.get('product', 'Solution')}
Prix cible: {context.get('target_price', '')}
Prix minimum: {context.get('minimum_price', '')}
Propositions de valeur: {', '.join(context.get('value_props', []))}

HISTORIQUE RÉCENT:
{history_context}

DERNIÈRE PHRASE OPPONENT:
"{transcript}"

PATTERN DÉTECTÉ:
{pattern['pattern']} (priorité: {pattern['priority']})
Suggestion auto: {pattern['suggestion']}

TACTIQUES SIMILAIRES:
{tactics_context}

GÉNÈRE:
1. Une suggestion tactique CONCRÈTE (max 12 mots, action immédiate)
2. Le type: "counter" (contrer), "warning" (alerte), ou "opportunity" (saisir)
3. Si auto-pilot est pertinent: quelle tactique appliquer?

Format JSON exact:
{{
    "suggestion": "💡 [Action très précise]",
    "type": "counter|warning|opportunity",
    "tactic": "counter_lowball|expose_urgency|firm_boundary|value_justification|confident_close|deflect_objection",
    "reasoning": "Courte explication (1 phrase)"
}}

RÈGLES:
- Suggestion DOIT commencer par emoji (💡 🛡️ ⚠️ ✅ 💰)
- Maximum 12 mots
- Action immédiate, pas de théorie
- Si opponent fait lowball → type="counter", tactic="counter_lowball"
- Si false urgency → type="warning", tactic="expose_urgency"
- Si signal positif → type="opportunity", tactic="confident_close"
"""

        try:
            response = self.mistral.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response.choices[0].message.content)

            # Determine if auto-pilot is available
            autopilot_available = result.get("tactic") in [
                "counter_lowball",
                "expose_urgency",
                "firm_boundary",
                "value_justification",
                "confident_close",
                "deflect_objection"
            ]

            return {
                "suggestion": result.get("suggestion", pattern["suggestion"]),
                "type": result.get("type", "counter"),
                "priority": pattern["priority"],
                "autopilot_available": autopilot_available,
                "tactic": result.get("tactic", pattern["response_type"]),
                "reasoning": result.get("reasoning", "Pattern détecté automatiquement"),
                "pattern_matched": pattern["pattern"],
                "confidence": pattern["confidence"]
            }

        except Exception as e:
            print(f"⚠️ Mistral analysis error: {e}")

            # Fallback to pattern-based suggestion
            return {
                "suggestion": pattern["suggestion"],
                "type": "warning" if pattern["priority"] == "critical" else "counter",
                "priority": pattern["priority"],
                "autopilot_available": True,
                "tactic": pattern["response_type"],
                "reasoning": "Suggestion basée sur pattern détecté",
                "pattern_matched": pattern["pattern"],
                "confidence": pattern["confidence"]
            }

    async def _generate_general_suggestion(
        self,
        transcript: str,
        speaker: str,
        context: Dict,
        history: Optional[List[Dict]]
    ) -> Dict:
        """Generate suggestion when no critical pattern detected"""

        if speaker == "opponent":
            # Opponent spoke, suggest a response approach
            return {
                "suggestion": "💬 Écoutez attentivement, prenez des notes",
                "type": "info",
                "priority": "medium",
                "autopilot_available": False,
                "tactic": None,
                "reasoning": "Pas de pattern critique, continuez la conversation"
            }
        else:
            # User spoke, provide light encouragement
            return {
                "suggestion": "✅ Bonne approche, continuez",
                "type": "info",
                "priority": "medium",
                "autopilot_available": False,
                "tactic": None,
                "reasoning": "Votre intervention semble appropriée"
            }

    def get_conversation_summary(self) -> Dict:
        """Get summary of detected patterns and conversation flow"""

        combo_analysis = self.pattern_detector.detect_combo_patterns(
            self.pattern_detector.conversation_history
        )

        all_patterns = []
        for turn in self.pattern_detector.conversation_history:
            all_patterns.extend(turn.get("patterns", []))

        pattern_counts = {}
        for p in all_patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1

        return {
            "total_turns": len(self.pattern_detector.conversation_history),
            "pattern_frequency": pattern_counts,
            "combo_detected": combo_analysis,
            "context_summary": self.pattern_detector.get_context_summary()
        }

    def reset(self):
        """Reset analyzer state for new conversation"""
        self.pattern_detector.reset()

"""
Endpoint webhook pour recevoir la transcription et les analytics d'ElevenLabs

ElevenLabs envoie les données post-appel à ce webhook :
- Transcription complète de la conversation
- Metadata (durée, status, etc.)
- Optionnel : Sentiment analysis

Structure reçue d'ElevenLabs :
{
    "call_id": str,
    "agent_id": str,
    "duration": int,
    "transcript": str,
    "status": "completed" | "failed",
    "metadata": {...}
}
"""

from fastapi import HTTPException
from typing import Dict
import json

async def analyze_negotiation_performance(
    transcript: str,
    user_context: Dict,
    mistral_service
) -> Dict:
    """
    Analyse la performance de négociation via Mistral AI

    Returns:
        {
            "score": int (0-100),
            "outcome": "success" | "partial" | "failure",
            "strengths": List[str],
            "weaknesses": List[str],
            "tactics_used": List[str],
            "price_negotiated": str | None,
            "recommendations": List[str]
        }
    """

    target_price = user_context.get('target_price', 'inconnu')
    minimum_price = user_context.get('minimum_price', 'inconnu')

    analysis_prompt = f"""Analysez cette négociation commerciale et évaluez la performance du vendeur.

CONTEXTE DE LA NÉGOCIATION:
- Prix demandé initialement : {target_price}
- Prix minimum acceptable : {minimum_price}
- Produit/Service : {user_context.get('product', 'Non spécifié')}

TRANSCRIPTION DE LA CONVERSATION:
{transcript}

TÂCHE: Analysez cette négociation et retournez un JSON avec:

1. **score** (0-100):
   - 90-100: Excellent - Objectif atteint, bonne marge préservée
   - 70-89: Bon - Accord trouvé avec compromis raisonnable
   - 50-69: Moyen - Accord mais trop de concessions
   - 30-49: Faible - Peu d'accord ou mauvaises conditions
   - 0-29: Échec - Pas d'accord ou conditions très défavorables

2. **outcome**: "success" | "partial" | "failure"

3. **strengths**: Liste de 2-3 points forts (tactiques efficaces, arguments solides, etc.)

4. **weaknesses**: Liste de 2-3 points faibles (concessions trop rapides, manque d'arguments, etc.)

5. **tactics_used**: Liste des tactiques de négociation identifiées dans la conversation

6. **price_negotiated**: Le prix final convenu (si accord), ou null

7. **recommendations**: Liste de 3-4 recommandations concrètes pour s'améliorer

Format: JSON valide seulement, pas de markdown."""

    try:
        print("🎯 Analyzing negotiation performance with Mistral...")

        response = mistral_service.client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        analysis = json.loads(response.choices[0].message.content)

        print(f"✅ Analysis completed - Score: {analysis.get('score', 0)}/100")
        print(f"   Outcome: {analysis.get('outcome', 'unknown')}")

        return analysis

    except Exception as e:
        print(f"❌ Negotiation analysis failed: {e}")
        return {
            "score": 50,
            "outcome": "unknown",
            "strengths": ["Conversation completed"],
            "weaknesses": ["Unable to analyze performance"],
            "tactics_used": [],
            "price_negotiated": None,
            "recommendations": ["Review conversation recording"]
        }

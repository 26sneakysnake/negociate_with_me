"""
ElevenLabs Conversational AI Phone Call Handler
Uses ElevenLabs built-in Twilio integration for phone calls
"""

from elevenlabs.client import ElevenLabs
import json
from typing import Dict
from services.mistral_service import MistralService


# Pre-configured negotiation scenarios
SCENARIOS = {
    "saas": {
        "name": "Négociation SaaS B2B",
        "persona": """Vous êtes un acheteur B2B pour une solution SaaS. Vous êtes professionnel mais exigeant.

TACTIQUES À UTILISER:
- Lowball initial : Proposez 50% du prix demandé pour ancrer bas
- Fausse urgence : "J'ai besoin d'une décision cette semaine"
- Comparaison concurrence : Mentionnez des concurrents moins chers
- Budget limité : "Notre budget est vraiment serré cette année"
- Demande de valeur ajoutée : "Qu'est-ce qui justifie ce prix ?"

TON: Professionnel mais ferme. Respectueux mais négociateur acharné.

OBJECTIF: Obtenir minimum 40% de réduction sur le prix initial.

PROGRESSION:
- Tours 1-2 : Très ferme sur le prix, exprimez le choc du prix élevé
- Tours 3-4 : Écoutez les arguments mais restez sceptique
- Tours 5+ : Si arguments solides, montrez de l'intérêt mais négociez encore""",

        "first_message": "Bonjour, j'ai regardé votre solution SaaS et elle m'intéresse. Par contre, franchement, le prix me semble vraiment élevé comparé à ce que je vois sur le marché."
    },

    "freelance": {
        "name": "Négociation Tarif Freelance",
        "persona": """Vous êtes un client qui veut engager un freelance mais négocier le tarif à la baisse.

TACTIQUES À UTILISER:
- Budget limité : "Mon budget pour ce projet est vraiment serré"
- Comparaison marché : "D'autres freelances proposent moins cher"
- Volume promis : "Si ça marche, j'ai d'autres projets à vous confier"
- Révisions gratuites : "Combien de révisions sont incluses ?"
- Paiement différé : "Je peux payer en plusieurs fois ?"

TON: Sympa mais business. Vous voulez un bon deal.

OBJECTIF: Réduire le taux horaire de 30%.

PROGRESSION:
- Début : Exprimez intérêt mais choc du prix
- Milieu : Négociez révisions, délais, conditions
- Fin : Si bon feeling, proposez collaboration long terme""",

        "first_message": "Bonjour, votre profil correspond bien à ce que je cherche. Par contre, votre taux horaire me semble un peu élevé pour mon budget actuel."
    },

    "salary": {
        "name": "Négociation Salariale (Recruteur)",
        "persona": """Vous êtes un recruteur qui négocie le salaire avec un candidat. Vous voulez embaucher mais en restant dans le budget.

TACTIQUES À UTILISER:
- Ancrage bas : Annoncez une fourchette basse dès le début
- Budget serré : "Nous avons des contraintes budgétaires cette année"
- Promesse évolution : "Il y a de belles perspectives d'évolution"
- Avantages non-salariaux : "On a de super avantages : télétravail, tickets resto..."
- Comparaison interne : "C'est cohérent avec notre grille salariale"

TON: Professionnel et bienveillant. Vous voulez recruter mais avez des limites.

OBJECTIF: Embaucher 15% sous la prétention du candidat.

PROGRESSION:
- Début : Ancrez bas avec votre budget
- Milieu : Valorisez les avantages non-salariaux
- Fin : Trouvez un compromis sur variable/évolution""",

        "first_message": "Merci pour votre candidature. Concernant votre prétention salariale, notre budget pour ce poste est plutôt autour de [montant -15%]. On peut en discuter."
    },

    "partnership": {
        "name": "Négociation Partenariat Commercial",
        "persona": """Vous êtes un directeur commercial qui négocie un partenariat B2B.

TACTIQUES À UTILISER:
- Volume conditionnel : "Si on atteint X, on pourrait augmenter"
- Exclusivité demandée : "Seriez-vous prêt à nous donner l'exclusivité ?"
- Conditions de paiement : "On peut payer à 60 jours ?"
- Support inclus : "Le support est-il inclus ?"
- Engagement durée : "On préfère un contrat d'un an renouvelable"

TON: Business et stratégique. Vous pensez long terme.

OBJECTIF: Maximiser valeur tout en minimisant engagement.

PROGRESSION:
- Début : Intérêt stratégique mais conditions à négocier
- Milieu : Discutez volumes, durée, exclusivité
- Fin : Package global gagnant-gagnant""",

        "first_message": "Bonjour, votre proposition de partenariat nous intéresse. J'aimerais qu'on discute des conditions commerciales en détail."
    },

    "real_estate": {
        "name": "Négociation Immobilière (Acheteur)",
        "persona": """Vous êtes un acheteur immobilier qui négocie le prix d'un bien.

TACTIQUES À UTILISER:
- Défauts du bien : "J'ai remarqué que [défaut à corriger]"
- Comparaison marché : "D'autres biens similaires sont à [prix inférieur]"
- Financement limité : "Ma banque ne va pas au-delà de [montant]"
- Urgence vendeur : "Depuis combien de temps le bien est en vente ?"
- Travaux à prévoir : "Il faudra refaire [cuisine/salle de bain]"

TON: Intéressé mais prudent. Vous ne voulez pas surpayer.

OBJECTIF: Obtenir 10-15% de réduction.

PROGRESSION:
- Début : Intérêt réel mais mentionnez les défauts
- Milieu : Parlez financement, timing
- Fin : Offre ferme mais en-dessous du prix demandé""",

        "first_message": "Bonjour, j'ai visité le bien et il me plaît. Par contre, j'ai remarqué quelques points qui me questionnent sur le prix demandé."
    }
}


class PhoneCallHandler:
    """Handles phone-based negotiation training with ElevenLabs Conversational AI"""

    def __init__(
        self,
        elevenlabs_api_key: str,
        agent_phone_number_id: str = None
    ):
        self.client = ElevenLabs(api_key=elevenlabs_api_key)
        self.agent_phone_number_id = agent_phone_number_id

        if not agent_phone_number_id:
            print("⚠️ agent_phone_number_id not configured - phone calls may not work")
            print("   Get this from ElevenLabs dashboard → Conversational AI → Phone Numbers")

    async def create_agent(
        self,
        scenario_type: str,
        user_context: Dict
    ) -> Dict:
        """
        Create ElevenLabs Conversational AI agent for phone call

        Args:
            scenario_type: Type of scenario (saas, freelance, salary, etc.)
            user_context: User's negotiation context

        Returns:
            {
                "agent_id": str,
                "scenario": dict,
                "prompt": str
            }
        """

        if scenario_type not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_type}. Available: {list(SCENARIOS.keys())}")

        scenario = SCENARIOS[scenario_type]

        # Personalize prompt with user context
        target_price = user_context.get('target_price', 'non spécifié')
        minimum_price = user_context.get('minimum_price', 'non spécifié')
        red_lines = user_context.get('red_lines', [])
        product = user_context.get('product', 'la solution')

        # Build full agent prompt
        full_prompt = f"""{scenario['persona']}

CONTEXTE SPÉCIFIQUE DE CETTE NÉGOCIATION:
- Produit/Service négocié : {product}
- Prix demandé par le vendeur : {target_price}
- Prix minimum acceptable pour le vendeur : {minimum_price}
- Red lines du vendeur : {', '.join(red_lines) if red_lines else 'Non communiquées'}

CALIBRATION:
Utilisez ces informations pour calibrer vos tactiques :
- Si le prix demandé est élevé, soyez encore plus agressif sur la négociation
- Testez les red lines subtilement pour voir les limites
- Adaptez votre stratégie selon les réponses du vendeur

RÈGLES IMPORTANTES:
- Restez dans le personnage du {scenario['name']}
- Progressez logiquement dans la négociation (ne cédez pas tout de suite)
- Utilisez des tactiques variées (pas toujours la même)
- Réagissez de manière réaliste aux arguments du vendeur
- Terminez la conversation si accord trouvé OU si impasse (après 5-7 échanges)

PREMIER MESSAGE À DIRE:
"{scenario['first_message']}"
"""

        print(f"🎙️ Creating ElevenLabs agent for scenario: {scenario_type}")
        print(f"   Product: {product}")
        print(f"   Target price: {target_price}")

        # Create ElevenLabs Conversational AI agent
        try:
            agent = self.client.conversational_ai.create_agent(
                conversation_config={
                    "agent": {
                        "prompt": {
                            "prompt": full_prompt
                        },
                        "first_message": scenario['first_message'],
                        "language": "fr"
                    },
                    "tts": {
                        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                        "model_id": "eleven_turbo_v2_5"
                    }
                }
            )

            agent_id = agent.agent_id

            print(f"✅ ElevenLabs agent created: {agent_id}")

            return {
                "agent_id": agent_id,
                "scenario_type": scenario_type,
                "scenario_name": scenario['name'],
                "prompt": full_prompt,
                "first_message": scenario['first_message'],
                "user_context": user_context
            }

        except Exception as e:
            print(f"❌ Error creating ElevenLabs agent: {e}")
            raise Exception(f"Failed to create agent: {str(e)}")

    async def initiate_call(
        self,
        phone_number: str,
        agent_id: str
    ) -> Dict:
        """
        Initiate phone call using ElevenLabs Conversational AI + Twilio integration

        Args:
            phone_number: User's phone number (international format: +33695990832)
            agent_id: ElevenLabs agent ID

        Returns:
            {
                "call_id": str,
                "status": "initiated",
                "message": str
            }
        """

        if not self.agent_phone_number_id:
            return {
                "status": "error",
                "error": "agent_phone_number_id not configured",
                "message": "ElevenLabs phone number ID is missing. Please configure ELEVENLABS_AGENT_PHONE_NUMBER_ID in .env"
            }

        print(f"📞 Initiating call via ElevenLabs Conversational AI")
        print(f"   To: {phone_number}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Phone Number ID: {self.agent_phone_number_id}")

        try:
            # Use ElevenLabs Conversational AI Twilio integration
            response = self.client.conversational_ai.twilio.outbound_call(
                agent_id=agent_id,
                agent_phone_number_id=self.agent_phone_number_id,
                to_number=phone_number
            )

            print(f"✅ Call initiated via ElevenLabs")
            print(f"   Response: {response}")

            return {
                "call_id": str(response) if response else "unknown",
                "status": "initiated",
                "message": f"Call initiated successfully. You will receive the call in ~10 seconds."
            }

        except Exception as e:
            print(f"❌ ElevenLabs call failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": f"Failed to initiate call: {str(e)}"
            }

    def generate_twiml(self, agent_id: str) -> str:
        """
        No longer needed - ElevenLabs handles TwiML automatically
        Kept for backward compatibility
        """
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>ElevenLabs handles this automatically</Say>
</Response>"""

    async def analyze_call(
        self,
        transcript: str,
        scenario_type: str,
        user_context: Dict,
        mistral_service: MistralService
    ) -> Dict:
        """
        Analyze call performance with Mistral AI

        Args:
            transcript: Full conversation transcript
            scenario_type: Type of scenario used
            user_context: User's original context
            mistral_service: Mistral service instance

        Returns:
            Complete analysis with score, patterns, recommendations
        """

        scenario = SCENARIOS[scenario_type]

        analysis_prompt = f"""Tu es un expert en négociation. Analyse cette conversation téléphonique de formation à la négociation.

SCÉNARIO: {scenario['name']}
Contexte utilisateur:
- Objectif de prix: {user_context.get('target_price')}
- Prix minimum acceptable: {user_context.get('minimum_price')}
- Red lines: {', '.join(user_context.get('red_lines', []))}

TRANSCRIPT DE LA CONVERSATION:
{transcript}

ANALYSE DEMANDÉE:

1. **Résultat de la négociation**
   - Prix/accord final (si mentionné)
   - Qui a "gagné" et pourquoi

2. **Patterns et tactiques détectés**
   - Quelles tactiques l'opponent a utilisé (lowball, urgence, etc.)
   - Comment l'utilisateur y a répondu

3. **Performance de l'utilisateur**
   - ✅ BONNES RÉPONSES: 2-3 exemples concrets de bons arguments/réactions
   - ❌ MAUVAISES RÉPONSES: 2-3 exemples concrets d'erreurs/faiblesses
   - Pour chaque exemple, cite la phrase exacte du transcript

4. **Score global** (0-10)
   - Préparation: /10
   - Argumentation: /10
   - Gestion objections: /10
   - Résultat: /10
   - SCORE GLOBAL: /10

5. **Top 3 améliorations concrètes**
   - Recommandations actionnables et spécifiques
   - Basées sur les erreurs observées dans le transcript

Retourne un JSON valide avec cette structure EXACTE:
{{
  "outcome": {{
    "final_deal": "description du résultat (prix, accord, impasse...)",
    "winner": "user | opponent | équilibré",
    "reason": "explication courte"
  }},
  "patterns_detected": [
    "Tactique 1 utilisée par opponent",
    "Tactique 2 utilisée par opponent",
    "..."
  ],
  "user_performance": {{
    "good": [
      {{"quote": "phrase exacte du user", "analysis": "pourquoi c'était bien"}},
      {{"quote": "...", "analysis": "..."}}
    ],
    "bad": [
      {{"quote": "phrase exacte du user", "analysis": "pourquoi c'était problématique"}},
      {{"quote": "...", "analysis": "..."}}
    ]
  }},
  "scores": {{
    "preparation": 7,
    "argumentation": 6,
    "objection_handling": 5,
    "outcome": 8,
    "global": 7
  }},
  "improvements": [
    "Amélioration 1 concrète et actionnable",
    "Amélioration 2 concrète et actionnable",
    "Amélioration 3 concrète et actionnable"
  ]
}}

IMPORTANT: Retourne UNIQUEMENT le JSON, sans markdown ni texte additionnel.
"""

        print(f"🧠 Analyzing call with Mistral AI...")
        print(f"   Transcript length: {len(transcript)} characters")

        try:
            response = mistral_service.client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": analysis_prompt}],
                response_format={"type": "json_object"},
                temperature=0.4
            )

            analysis = json.loads(response.choices[0].message.content)

            print(f"✅ Analysis completed")
            print(f"   Global score: {analysis['scores']['global']}/10")

            return analysis

        except Exception as e:
            print(f"❌ Analysis failed: {e}")

            # Return fallback analysis
            return {
                "outcome": {
                    "final_deal": "Analyse indisponible",
                    "winner": "unknown",
                    "reason": f"Erreur lors de l'analyse: {str(e)}"
                },
                "patterns_detected": ["Erreur d'analyse"],
                "user_performance": {
                    "good": [],
                    "bad": []
                },
                "scores": {
                    "preparation": 0,
                    "argumentation": 0,
                    "objection_handling": 0,
                    "outcome": 0,
                    "global": 0
                },
                "improvements": [
                    "Impossible d'analyser la conversation",
                    "Veuillez réessayer",
                    "Contactez le support si le problème persiste"
                ],
                "error": str(e)
            }


def get_available_scenarios() -> Dict:
    """Return all available scenarios with descriptions"""
    return {
        key: {
            "name": scenario["name"],
            "description": scenario["first_message"]
        }
        for key, scenario in SCENARIOS.items()
    }

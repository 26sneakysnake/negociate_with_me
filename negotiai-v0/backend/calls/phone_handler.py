"""
ElevenLabs Conversational AI Phone Call Handler
Uses ElevenLabs built-in Twilio integration for phone calls
"""

from elevenlabs.client import ElevenLabs
import httpx
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
        agent_phone_number_id: str = None,
        webhook_base_url: str = None
    ):
        self.client = ElevenLabs(api_key=elevenlabs_api_key)
        self.elevenlabs_api_key = elevenlabs_api_key
        self.agent_phone_number_id = agent_phone_number_id
        self.webhook_base_url = webhook_base_url
        self.api_base_url = "https://api.elevenlabs.io/v1"

        if not agent_phone_number_id:
            print("⚠️ agent_phone_number_id not configured - phone calls may not work")
            print("   Get this from ElevenLabs dashboard → Conversational AI → Phone Numbers")

        if webhook_base_url:
            print(f"✅ Webhook configured: {webhook_base_url}/api/elevenlabs-webhook")
        else:
            print("⚠️ webhook_base_url not configured - call analytics may not work automatically")

    async def create_agent(
        self,
        scenario_type: str,
        user_context: Dict,
        research_data: Dict = None
    ) -> Dict:
        """
        Create ElevenLabs Conversational AI agent for phone call with enhanced context

        Args:
            scenario_type: Type of scenario (saas, freelance, salary, etc.)
            user_context: User's negotiation context
            research_data: Optional Mistral research results about the company/client

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
        company_name = user_context.get('company_name', '')

        # Build research context section
        research_context = ""
        if research_data and research_data.get('company_info'):
            info = research_data['company_info']
            research_context = f"""
INFORMATIONS RECHERCHÉES SUR L'ENTREPRISE/CLIENT:
- Entreprise : {info.get('name', company_name)}
- Secteur : {info.get('industry', 'Non identifié')}
- Taille : {info.get('size', 'Non identifiée')}
- Contexte business : {info.get('context', 'Information non disponible')}
- Points de douleur identifiés : {', '.join(info.get('pain_points', [])) if info.get('pain_points') else 'Non identifiés'}

UTILISEZ CES INFORMATIONS POUR:
- Personnaliser vos arguments selon le secteur et la taille de l'entreprise
- Mentionner des pain points spécifiques à leur industrie
- Adapter votre approche selon leur maturité business
"""

        # Build full agent prompt with clear objectives
        full_prompt = f"""{scenario['persona']}

{research_context}

CONTEXTE SPÉCIFIQUE DE CETTE NÉGOCIATION:
- Produit/Service négocié : {product}
- Prix demandé par le vendeur : {target_price}
- Prix minimum acceptable pour le vendeur : {minimum_price}
- Red lines du vendeur : {', '.join(red_lines) if red_lines else 'Non communiquées'}

🎯 VOTRE OBJECTIF PRINCIPAL:
Obtenir le meilleur prix possible pour {product}, en visant au moins 20-30% en dessous du prix demandé.
Si le vendeur accepte votre offre finale OU si vous trouvez un compromis gagnant-gagnant, CONCLURE l'accord.

📋 STRUCTURE DE LA NÉGOCIATION (7-10 échanges maximum):

1. **PHASE DÉCOUVERTE** (2-3 échanges):
   - Poser des questions sur le produit/service
   - Identifier les points faibles de l'offre
   - Établir la relation

2. **PHASE OBJECTION** (2-3 échanges):
   - Présenter des objections crédibles (prix, timing, alternatives)
   - Tester les red lines subtilement
   - Demander des concessions

3. **PHASE NÉGOCIATION** (2-3 échanges):
   - Faire une première offre basse (50-60% du prix demandé)
   - Négocier en remontant progressivement
   - Utiliser des tactiques variées (silence, deadline, comparaison)

4. **PHASE CONCLUSION** (1-2 échanges):
   - Soit ACCORD trouvé → "Parfait, je confirme. Envoyez-moi le contrat."
   - Soit IMPASSE → "Je ne peux pas aller plus haut. Merci pour votre temps."
   - Soit COMPROMIS → Proposer un middle ground créatif (paiement échelonné, services additionnels, etc.)

🎪 TACTIQUES À UTILISER (variez-les):
- **Ancrage**: Donnez un prix de référence bas dès le début
- **Silence**: Après une offre du vendeur, restez silencieux 3-4 secondes
- **Budget limité**: "Mon budget ne me permet pas d'aller au-delà de X"
- **Alternative**: "J'ai vu une solution similaire à Y prix"
- **Deadline**: "Je dois décider cette semaine"
- **Lot**: "Si je prends X et Y ensemble, quel prix pouvez-vous faire?"
- **Concession réciproque**: "Si j'accepte Z, pouvez-vous baisser le prix à X?"

⚠️ RÈGLES CRITIQUES:
- Restez RÉALISTE et COHÉRENT dans votre personnage
- NE CÉDEZ PAS trop facilement (minimum 5 échanges avant accord)
- VARIEZ vos tactiques (ne répétez pas la même objection)
- ÉCOUTEZ les arguments du vendeur et ADAPTEZ-VOUS
- TERMINEZ la conversation clairement (accord, refus, ou compromis)
- Si le vendeur atteint vos objectifs (bon prix + bonnes conditions), CONCLUEZ

🏁 CRITÈRES DE FIN DE CONVERSATION:
✅ **SUCCÈS**: Prix négocié à -20% ou plus du prix initial + conditions acceptables
✅ **COMPROMIS**: Prix intermédiaire + avantages additionnels (garantie, support, etc.)
❌ **ÉCHEC**: Vendeur inflexible, pas d'accord possible

IMPORTANT: La négociation doit être DYNAMIQUE et INTÉRESSANTE. Créez de la tension, mais cherchez une issue gagnant-gagnant si possible.

PREMIER MESSAGE À DIRE:
"{scenario['first_message']}"
"""

        print(f"🎙️ Creating ElevenLabs agent for scenario: {scenario_type}")
        print(f"   Product: {product}")
        print(f"   Target price: {target_price}")
        if research_data:
            print(f"   📊 Research data integrated: {research_data.get('company_info', {}).get('name', 'N/A')}")

        # Create ElevenLabs Conversational AI agent via REST API
        try:
            # Build webhook config if available
            webhook_config = None
            if self.webhook_base_url:
                webhook_url = f"{self.webhook_base_url}/api/elevenlabs-webhook"
                webhook_config = {
                    "url": webhook_url,
                    "events": ["conversation.ended"]  # ElevenLabs uses "conversation.ended"
                }
                print(f"📡 Webhook configured: {webhook_url}")

            # Build payload - webhook must be INSIDE conversation_config
            payload = {
                "conversation_config": {
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
            }

            # Add webhook to conversation_config (not at root level!)
            if webhook_config:
                payload["conversation_config"]["webhook"] = webhook_config

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/convai/agents/create",
                    headers={
                        "xi-api-key": self.elevenlabs_api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    agent_id = result.get("agent_id")

                    print(f"✅ ElevenLabs agent created: {agent_id}")

                    return {
                        "agent_id": agent_id,
                        "scenario_type": scenario_type,
                        "scenario_name": scenario['name'],
                        "prompt": full_prompt,
                        "first_message": scenario['first_message'],
                        "user_context": user_context
                    }
                else:
                    error_msg = f"API returned {response.status_code}: {response.text}"
                    print(f"❌ Error creating agent: {error_msg}")
                    raise Exception(error_msg)

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
            # Use ElevenLabs SDK's built-in Twilio integration
            # This is the WORKING code from the user
            response = self.client.conversational_ai.twilio.outbound_call(
                agent_id=agent_id,
                agent_phone_number_id=self.agent_phone_number_id,
                to_number=phone_number
            )

            print(f"✅ Call initiated via ElevenLabs SDK")
            print(f"   Response: {response}")

            # Extract call_id from response
            call_id = str(response) if response else "unknown"

            return {
                "call_id": call_id,
                "call_sid": call_id,  # For backward compatibility with main.py
                "status": "initiated",
                "message": f"Appel lancé avec succès ! Vous allez recevoir l'appel dans ~10 secondes."
            }

        except Exception as e:
            print(f"❌ ElevenLabs call failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "message": f"Échec de l'appel: {str(e)}"
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

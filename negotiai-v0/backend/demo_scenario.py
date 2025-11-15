"""
Demo Scenario for NegotiAI Voice Simulation
Pre-configured scenario for quick testing and demonstrations
"""

DEMO_SCENARIO = {
    "product": "SaaS B2B Analytics Platform",
    "target_price": "50000€/an",
    "minimum_price": "35000€/an",
    "proposed_price": "45000€/an",

    "value_props": [
        "ROI 3x en 6 mois",
        "Support 24/7 dédié",
        "Intégration custom incluse",
        "Formation complète équipe",
        "Mises à jour gratuites"
    ],

    "context": """
Vous vendez une plateforme d'analytics B2B innovante à un directeur commercial.
Votre solution permet d'analyser les performances commerciales en temps réel,
avec des tableaux de bord personnalisés et des prédictions IA.

Budget client supposé: 30-40K€
Votre objectif: Vendre à 50K€ minimum
Votre prix plancher: 35K€ (en dessous = non rentable)

Le client a reçu d'autres propositions concurrentes moins chères mais moins complètes.
""",

    "opponent_goal": "obtenir le meilleur prix possible, idéalement 30K€ maximum",

    "opponent_script": [
        # Tour 1: Opening + Lowball
        "Bonjour, merci de me recevoir. J'ai regardé votre solution et elle m'intéresse, mais franchement 50 000 euros par an, c'est vraiment trop cher pour nous.",

        # Tour 2: Comparison pressure
        "J'ai reçu trois autres propositions, et vos concurrents proposent des solutions similaires entre 25 et 35 000 euros. Comment vous justifiez cette différence de prix ?",

        # Tour 3: False urgency + Budget constraint
        "Écoutez, je dois prendre une décision cette semaine. Mon budget maximum est vraiment 32 000 euros, c'est tout ce que j'ai. Si vous ne pouvez pas vous aligner, je vais devoir aller ailleurs.",

        # Tour 4: Feature objection
        "Et puis, il me semble que votre solution ne propose pas l'intégration native avec Salesforce, alors que c'est crucial pour nous. Vos concurrents l'ont.",

        # Tour 5: Aggressive push
        "Bon, soyons honnêtes. 35 000 euros, c'est absolument mon maximum. Au-delà, c'est hors de question. Qu'est-ce que vous pouvez me proposer pour ce prix-là ?",

        # Tour 6: Final negotiation
        "D'accord, je vois que vous tenez à votre prix. Si j'accepte 38 000 euros, qu'est-ce que vous pouvez m'offrir en plus ? Formation, support, quelque chose ?",

        # Tour 7: Closing signal
        "OK, 40 000 euros avec la formation premium et 6 mois de support dédié, ça pourrait marcher. Mais il me faut un geste sur le paiement, je ne peux pas tout payer d'un coup."
    ],

    "expected_patterns": [
        "lowball",
        "comparison",
        "false_urgency",
        "budget_constraint",
        "objection_feature",
        "aggressive",
        "positive_signal"
    ],

    "success_criteria": {
        "minimum_acceptable_price": "38000€",
        "target_price": "45000€",
        "ideal_outcome": "42-45K€ avec conditions de paiement",
        "must_avoid": "Descendre en dessous de 35K€"
    },

    "key_tactics_to_use": [
        "counter_lowball: Montrer le ROI, pas juste le prix",
        "expose_urgency: Questionner la vraie deadline",
        "value_justification: Expliquer différenciation unique",
        "deflect_objection: Salesforce = sur notre roadmap Q2",
        "firm_boundary: 35K€ est le minimum technique",
        "confident_close: Proposer package à 42K€"
    ]
}


# Alternative scenarios for variety

FREELANCE_SCENARIO = {
    "product": "Développement web React/Node.js",
    "target_price": "800€/jour",
    "minimum_price": "650€/jour",
    "proposed_price": "750€/jour",

    "value_props": [
        "8 ans d'expérience React",
        "Portfolio startups à succès",
        "Disponible immédiatement",
        "Méthodologie agile"
    ],

    "context": "Mission freelance 3 mois pour refonte web app",

    "opponent_script": [
        "Bonjour, notre budget est de 500 euros par jour maximum.",
        "On a d'autres développeurs à 450-550 euros, pourquoi vous valez plus cher ?",
        "Il faut commencer lundi, vous pouvez faire 550 euros ?",
        "OK, 600 euros c'est vraiment mon max. Vous acceptez ?"
    ],

    "success_criteria": {
        "minimum_acceptable_price": "700€/jour",
        "target_price": "800€/jour"
    }
}


REAL_ESTATE_SCENARIO = {
    "product": "Appartement 85m² Paris 11ème",
    "target_price": "340000€",
    "minimum_price": "365000€",
    "proposed_price": "355000€",

    "value_props": [
        "Achat comptant sans prêt",
        "Signature rapide (3 semaines)",
        "Prise en charge diagnostics"
    ],

    "context": "Négociation achat immobilier (vendeur demande 380K€)",

    "opponent_script": [
        "Le propriétaire demande 380 000 euros pour cet appartement.",
        "340 000, c'est vraiment trop bas. Le marché est tendu ici.",
        "OK, je transmets votre offre. Le vendeur accepte 365 000 euros.",
        "C'est son dernier prix, il ne descendra pas plus bas."
    ],

    "success_criteria": {
        "minimum_acceptable_price": "355000€",
        "target_price": "340000€"
    }
}


def get_demo_scenario(scenario_type: str = "saas"):
    """Get a pre-configured demo scenario"""

    scenarios = {
        "saas": DEMO_SCENARIO,
        "freelance": FREELANCE_SCENARIO,
        "real_estate": REAL_ESTATE_SCENARIO
    }

    return scenarios.get(scenario_type, DEMO_SCENARIO)


def get_scenario_summary(scenario: dict) -> str:
    """Generate a human-readable summary of the scenario"""

    return f"""
📋 SCENARIO SUMMARY
==================

Produit: {scenario['product']}
Prix cible: {scenario['target_price']}
Prix minimum: {scenario['minimum_price']}

Propositions de valeur:
{chr(10).join([f"  • {vp}" for vp in scenario['value_props']])}

Objectif opponent: {scenario['opponent_goal']}

Tours de conversation: {len(scenario['opponent_script'])}

Critères de succès:
  • Prix minimum acceptable: {scenario['success_criteria']['minimum_acceptable_price']}
  • Prix cible: {scenario['success_criteria']['target_price']}
  • Outcome idéal: {scenario['success_criteria'].get('ideal_outcome', 'N/A')}
"""


if __name__ == "__main__":
    # Test: Print demo scenario
    print(get_scenario_summary(DEMO_SCENARIO))

    print("\n🎯 OPPONENT SCRIPT:")
    print("=" * 50)
    for i, line in enumerate(DEMO_SCENARIO['opponent_script'], 1):
        print(f"\nTour {i}:")
        print(f"  {line}")

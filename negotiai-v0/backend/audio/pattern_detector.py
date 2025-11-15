"""
Real-time Pattern Detection for Negotiation Tactics
Detects critical patterns in conversation for instant suggestions
"""

from typing import List, Dict
import re


# Critical negotiation patterns with response strategies
CRITICAL_PATTERNS = {
    "lowball": {
        "keywords": [
            "trop cher", "cher", "expensive", "prix élevé",
            "concurrent", "competition", "moins cher", "cheaper",
            "budget", "afford", "can't pay"
        ],
        "phrases": [
            "c'est trop", "that's too much", "way too expensive",
            "autre offre", "other offer", "better price"
        ],
        "response_type": "counter_lowball",
        "priority": "high",
        "suggestion": "💡 Comparaison de prix détectée → Parlez ROI, pas prix"
    },

    "false_urgency": {
        "keywords": [
            "aujourd'hui", "today", "maintenant", "now",
            "immédiatement", "immediately", "urgent", "deadline"
        ],
        "phrases": [
            "besoin maintenant", "need now", "expire", "dernière offre",
            "last offer", "limited time", "aujourd'hui seulement",
            "il faut décider"
        ],
        "response_type": "expose_urgency",
        "priority": "critical",
        "suggestion": "⚠️ FAUSSE URGENCE → Demandez: 'Quelle est la vraie deadline?'"
    },

    "aggressive": {
        "keywords": [
            "impossible", "jamais", "never", "hors de question",
            "no way", "ridiculous", "absurde"
        ],
        "phrases": [
            "je ne peux pas", "can't do", "won't work",
            "c'est non", "that's a no", "absolument pas"
        ],
        "response_type": "calm_and_firm",
        "priority": "critical",
        "suggestion": "🛡️ RÉSISTANCE FORTE → Restez calme, reformulez votre valeur"
    },

    "budget_constraint": {
        "keywords": [
            "budget maximum", "max budget", "limite", "limit",
            "pas plus", "no more", "plafond", "ceiling"
        ],
        "phrases": [
            "mon budget est", "my budget is", "je peux offrir",
            "maximum je peux", "most I can", "c'est tout ce que"
        ],
        "response_type": "firm_boundary",
        "priority": "high",
        "suggestion": "💰 CONTRAINTE BUDGET → Proposez options de paiement ou package"
    },

    "objection_feature": {
        "keywords": [
            "manque", "missing", "n'a pas", "doesn't have",
            "pas de", "no", "feature", "fonctionnalité"
        ],
        "phrases": [
            "votre solution n'a pas", "your solution doesn't",
            "il manque", "missing", "j'ai besoin de", "I need"
        ],
        "response_type": "deflect_objection",
        "priority": "high",
        "suggestion": "🔧 OBJECTION FEATURE → Montrez alternatives ou roadmap"
    },

    "comparison": {
        "keywords": [
            "concurrent", "competitor", "autre", "other",
            "vs", "versus", "compare", "comparé"
        ],
        "phrases": [
            "concurrent fait", "competitor does", "autre solution",
            "other solution", "chez eux", "with them"
        ],
        "response_type": "value_justification",
        "priority": "medium",
        "suggestion": "📊 COMPARAISON → Expliquez votre différenciation unique"
    },

    "hesitation_user": {
        "keywords": [
            "peut-être", "maybe", "je ne sais pas", "don't know",
            "il faudrait", "would need", "euh", "um", "hésitant"
        ],
        "phrases": [
            "pas sûr", "not sure", "je dois réfléchir",
            "need to think", "voir", "check"
        ],
        "response_type": "confident_close",
        "priority": "medium",
        "suggestion": "💪 HÉSITATION DÉTECTÉE → Soyez confiant et précis",
        "detection_source": "user"  # This pattern detects user's hesitation
    },

    "positive_signal": {
        "keywords": [
            "intéressant", "interesting", "j'aime", "I like",
            "bon point", "good point", "je vois", "I see",
            "d'accord", "okay"
        ],
        "phrases": [
            "ça m'intéresse", "sounds good", "tell me more",
            "c'est vrai", "that's true", "vous avez raison"
        ],
        "response_type": "close_opportunity",
        "priority": "high",
        "suggestion": "✅ SIGNAL POSITIF → C'est le moment de closer!",
        "is_opportunity": True
    },

    "price_anchor_set": {
        "keywords": ["offrir", "offer", "proposer", "propose"],
        "phrases": [
            "je peux faire", "I can do", "je propose",
            "my offer is", "willing to pay"
        ],
        "response_type": "evaluate_anchor",
        "priority": "critical",
        "suggestion": "⚓ ANCRAGE PRIX → Évaluez si acceptable ou counter"
    }
}


class PatternDetector:
    """Detects critical patterns in real-time conversation"""

    def __init__(self):
        self.patterns = CRITICAL_PATTERNS
        self.conversation_history = []

    def detect(self, transcript: str, speaker: str = "opponent") -> List[Dict]:
        """
        Detect patterns in a transcript snippet

        Args:
            transcript: Text to analyze
            speaker: "opponent" or "user"

        Returns:
            List of detected patterns with metadata:
            [{
                "pattern": str,
                "priority": "critical"|"high"|"medium",
                "response_type": str,
                "suggestion": str,
                "confidence": float
            }]
        """

        text_lower = transcript.lower()
        detected = []

        for pattern_name, pattern_data in self.patterns.items():
            # Skip user-hesitation pattern if opponent is speaking
            if pattern_data.get("detection_source") == "user" and speaker != "user":
                continue

            confidence = 0.0
            matched_items = []

            # Check keywords
            for keyword in pattern_data.get("keywords", []):
                if keyword.lower() in text_lower:
                    confidence += 0.3
                    matched_items.append(keyword)

            # Check phrases (higher weight)
            for phrase in pattern_data.get("phrases", []):
                if phrase.lower() in text_lower:
                    confidence += 0.5
                    matched_items.append(phrase)

            # If pattern detected with sufficient confidence
            if confidence > 0.3:
                detected.append({
                    "pattern": pattern_name,
                    "priority": pattern_data["priority"],
                    "response_type": pattern_data["response_type"],
                    "suggestion": pattern_data["suggestion"],
                    "confidence": min(confidence, 1.0),
                    "matched_items": matched_items[:3],  # Top 3 matches
                    "is_opportunity": pattern_data.get("is_opportunity", False)
                })

        # Sort by priority and confidence
        priority_order = {"critical": 3, "high": 2, "medium": 1}
        detected.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]),
            reverse=True
        )

        # Store in history for context
        self.conversation_history.append({
            "speaker": speaker,
            "text": transcript,
            "patterns": [d["pattern"] for d in detected]
        })

        return detected

    def detect_combo_patterns(self, recent_turns: List[Dict]) -> Dict:
        """
        Detect pattern combinations across multiple turns
        E.g., lowball + urgency = very aggressive negotiation

        Args:
            recent_turns: Last N conversation turns with patterns

        Returns:
            {
                "combo_type": str,
                "severity": str,
                "recommendation": str
            }
        """

        if len(recent_turns) < 2:
            return {}

        # Extract all patterns from recent turns
        all_patterns = []
        for turn in recent_turns[-3:]:  # Last 3 turns
            all_patterns.extend(turn.get("patterns", []))

        # Detect dangerous combos
        if "lowball" in all_patterns and "false_urgency" in all_patterns:
            return {
                "combo_type": "aggressive_squeeze",
                "severity": "critical",
                "recommendation": "⚠️ COMBO AGRESSIF détecté (Prix + Urgence) → Exposez les tactiques calmement"
            }

        if "aggressive" in all_patterns and "budget_constraint" in all_patterns:
            return {
                "combo_type": "hard_negotiator",
                "severity": "high",
                "recommendation": "🎯 Négociateur dur → Tenez bon sur votre prix minimum"
            }

        if all_patterns.count("objection_feature") >= 2:
            return {
                "combo_type": "feature_focused",
                "severity": "medium",
                "recommendation": "🔍 Focus features → Recentrez sur la valeur business, pas les features"
            }

        if "positive_signal" in all_patterns and len(all_patterns) > 0:
            return {
                "combo_type": "closing_window",
                "severity": "high",
                "recommendation": "✨ FENÊTRE DE CLOSING → Proposez un deal maintenant!"
            }

        return {}

    def get_context_summary(self, last_n: int = 5) -> str:
        """
        Get summary of recent conversation context

        Args:
            last_n: Number of recent turns to summarize

        Returns:
            Summary string
        """

        recent = self.conversation_history[-last_n:]

        summary_parts = []
        for turn in recent:
            speaker_label = "👤 Vous" if turn["speaker"] == "user" else "🤝 Client"
            patterns_str = ", ".join(turn["patterns"]) if turn["patterns"] else "normal"
            summary_parts.append(f"{speaker_label}: {turn['text'][:50]}... [{patterns_str}]")

        return "\n".join(summary_parts)

    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []

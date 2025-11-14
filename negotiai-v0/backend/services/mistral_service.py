# backend/services/mistral_service.py
from mistralai import Mistral
from backend.config import get_settings
from backend.models import Strategy, Objection, Analysis, TacticDetection, PerformanceScore
import json
from typing import List
import uuid

class MistralService:
    def __init__(self):
        settings = get_settings()
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)
        self.model = settings.MISTRAL_MODEL

    async def generate_strategy(
        self,
        context_text: str,
        objective: str,
        minimum: str,
        counterparty: str,
        tactics_context: List[str]
    ) -> Strategy:
        """Generate complete negotiation strategy"""

        # Build prompt with tactics context
        tactics_str = "\n".join([f"- {t}" for t in tactics_context])

        prompt = f"""You are an expert negotiation strategist. Analyze this negotiation context and create a comprehensive strategy.

CONTEXT:
{context_text}

OBJECTIVE: {objective}
MINIMUM ACCEPTABLE: {minimum}
COUNTERPARTY: {counterparty or "Unknown"}

AVAILABLE TACTICS FOR REFERENCE:
{tactics_str}

Generate a detailed negotiation strategy in JSON format with:
1. summary: One paragraph overview of the situation
2. opening_position: Your initial offer/position
3. key_arguments: 4-5 strongest arguments supporting your position
4. concession_plan: 3-4 steps of progressive concessions if needed
5. red_lines: 2-3 absolute deal-breakers
6. expected_objections: 4-5 likely objections with counter-arguments (include confidence 0-1)
7. batna: Your best alternative if this negotiation fails

Return ONLY valid JSON matching this structure:
{{
  "summary": "...",
  "opening_position": "...",
  "key_arguments": ["...", "..."],
  "concession_plan": ["...", "..."],
  "red_lines": ["...", "..."],
  "expected_objections": [
    {{"objection": "...", "counter_argument": "...", "confidence": 0.8}}
  ],
  "batna": "..."
}}"""

        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        strategy_data = json.loads(response.choices[0].message.content)

        # Build Strategy object
        return Strategy(
            session_id=str(uuid.uuid4()),
            summary=strategy_data["summary"],
            opening_position=strategy_data["opening_position"],
            key_arguments=strategy_data["key_arguments"],
            concession_plan=strategy_data["concession_plan"],
            red_lines=strategy_data["red_lines"],
            expected_objections=[
                Objection(**obj) for obj in strategy_data["expected_objections"]
            ],
            batna=strategy_data["batna"]
        )

    async def analyze_negotiation(
        self,
        strategy: Strategy,
        transcript: str,
        actual_outcome: str,
        tactics_context: List[str]
    ) -> Analysis:
        """Analyze negotiation performance"""

        tactics_str = "\n".join([f"- {t}" for t in tactics_context])

        prompt = f"""You are an expert negotiation coach. Analyze this completed negotiation.

ORIGINAL STRATEGY:
Objective: {strategy.opening_position}
Key Arguments: {', '.join(strategy.key_arguments)}
Red Lines: {', '.join(strategy.red_lines)}

TRANSCRIPT:
{transcript}

ACTUAL OUTCOME: {actual_outcome}

KNOWN TACTICS FOR REFERENCE:
{tactics_str}

Analyze the performance and return JSON with:
1. performance: Scores 0-100 for overall, preparation, tactics, outcome
2. tactics_used: 5-8 detected tactics with:
   - tactic_name, tactic_type (offensive/defensive/neutral)
   - quote (exact phrase), effectiveness (excellent/good/poor/missed_opportunity)
   - explanation
3. strengths: 3-4 things done well
4. weaknesses: 3-4 areas for improvement
5. key_recommendations: 3-4 actionable tips for next time

Return ONLY valid JSON:
{{
  "performance": {{
    "overall_score": 75,
    "preparation_score": 80,
    "tactics_score": 70,
    "outcome_score": 75
  }},
  "tactics_used": [
    {{
      "tactic_name": "Anchoring",
      "tactic_type": "offensive",
      "quote": "exact phrase from transcript",
      "effectiveness": "good",
      "explanation": "..."
    }}
  ],
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "key_recommendations": ["...", "..."]
}}"""

        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        analysis_data = json.loads(response.choices[0].message.content)

        return Analysis(
            session_id=strategy.session_id,
            performance=PerformanceScore(**analysis_data["performance"]),
            tactics_used=[
                TacticDetection(**tactic) for tactic in analysis_data["tactics_used"]
            ],
            strengths=analysis_data["strengths"],
            weaknesses=analysis_data["weaknesses"],
            key_recommendations=analysis_data["key_recommendations"]
        )

    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        response = self.client.embeddings.create(
            model="mistral-embed",
            inputs=[text]
        )
        return response.data[0].embedding

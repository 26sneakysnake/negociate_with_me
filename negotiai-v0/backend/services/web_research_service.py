"""
Web Research Service for Negotiation Context Enhancement
Uses web search to gather information about products and clients
"""

import asyncio
from typing import Dict, List
import json


class WebResearchService:
    """Gathers contextual information via web search before negotiation"""

    def __init__(self, mistral_service):
        self.mistral = mistral_service

    async def research_solution(self, product_name: str, industry: str = None) -> Dict:
        """
        Research a product/solution on the web

        Args:
            product_name: Name of the product/service to research
            industry: Industry/sector (optional)

        Returns:
            {
                "features": List[str],
                "typical_pricing": str,
                "competitors": List[str],
                "market_position": str,
                "key_benefits": List[str]
            }
        """

        # Note: For MVP, we'll use Mistral's general knowledge
        # In production, integrate with a real web search API (Serper, Tavily, etc.)

        query = f"""Based on your knowledge, provide information about "{product_name}" {f"in the {industry} industry" if industry else ""}.

Return a JSON with:
- features: List of 3-5 key features
- typical_pricing: Typical market pricing range
- competitors: List of 2-3 main competitors
- market_position: Brief description of market positioning
- key_benefits: List of 3 main benefits for customers

Format: Valid JSON only, no markdown."""

        try:
            print(f"🔍 Calling Mistral API for product research: {product_name}")
            response = self.mistral.client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": query}],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            print(f"📥 Received response from Mistral API")
            print(f"   Raw content: {response.choices[0].message.content[:200]}...")

            research_data = json.loads(response.choices[0].message.content)
            print(f"✅ Solution research completed for: {product_name}")
            print(f"   Features found: {len(research_data.get('features', []))}")
            print(f"   Competitors found: {len(research_data.get('competitors', []))}")

            return research_data

        except Exception as e:
            print(f"❌ Web research failed with exception: {type(e).__name__}")
            print(f"❌ Error details: {str(e)}")
            import traceback
            print(f"❌ Traceback:\n{traceback.format_exc()}")
            return {
                "features": ["Feature 1", "Feature 2", "Feature 3"],
                "typical_pricing": "Market rate",
                "competitors": ["Competitor A", "Competitor B"],
                "market_position": "Competitive solution",
                "key_benefits": ["Benefit 1", "Benefit 2", "Benefit 3"]
            }

    async def research_client(self, company_name: str, industry: str = None) -> Dict:
        """
        Research a client company

        Args:
            company_name: Name of the client company
            industry: Industry/sector (optional)

        Returns:
            {
                "company_size": str,
                "industry": str,
                "pain_points": List[str],
                "budget_range": str,
                "decision_factors": List[str]
            }
        """

        query = f"""Based on your knowledge, provide information about "{company_name}" {f"in the {industry} sector" if industry else ""} as a potential B2B client.

Return a JSON with:
- company_size: Estimated size (startup, SME, enterprise)
- industry: Main industry/sector
- pain_points: List of 2-3 typical pain points for this type of company
- budget_range: Estimated budget range for B2B solutions
- decision_factors: List of 2-3 key factors in their buying decisions

Format: Valid JSON only, no markdown."""

        try:
            print(f"🔍 Calling Mistral API for client research: {company_name}")
            response = self.mistral.client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": query}],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            print(f"📥 Received response from Mistral API")
            print(f"   Raw content: {response.choices[0].message.content[:200]}...")

            client_data = json.loads(response.choices[0].message.content)
            print(f"✅ Client research completed for: {company_name}")
            print(f"   Company size: {client_data.get('company_size')}")
            print(f"   Industry: {client_data.get('industry')}")

            return client_data

        except Exception as e:
            print(f"❌ Client research failed with exception: {type(e).__name__}")
            print(f"❌ Error details: {str(e)}")
            import traceback
            print(f"❌ Traceback:\n{traceback.format_exc()}")
            return {
                "company_size": "SME",
                "industry": industry or "Technology",
                "pain_points": ["Cost optimization", "Efficiency"],
                "budget_range": "Medium",
                "decision_factors": ["ROI", "Support quality"]
            }

    async def prepare_negotiation_context(
        self,
        product_name: str,
        company_name: str = None,
        industry: str = None
    ) -> Dict:
        """
        Prepare comprehensive negotiation context with web research

        Args:
            product_name: Product/service being sold
            company_name: Client company name (optional)
            industry: Industry sector (optional)

        Returns:
            Complete enriched context for negotiation
        """

        print(f"🔍 Starting web research...")
        print(f"   Product: {product_name}")
        if company_name:
            print(f"   Client: {company_name}")

        # Run both researches in parallel
        tasks = [
            self.research_solution(product_name, industry)
        ]

        if company_name:
            tasks.append(self.research_client(company_name, industry))

        results = await asyncio.gather(*tasks)

        solution_data = results[0]
        client_data = results[1] if len(results) > 1 else None

        # Build enriched context
        enriched_context = {
            "product": {
                "name": product_name,
                **solution_data
            }
        }

        if client_data:
            enriched_context["client"] = {
                "name": company_name,
                **client_data
            }

        print("✅ Research completed!")
        print(f"   - Features identified: {len(solution_data.get('features', []))}")
        print(f"   - Competitors found: {len(solution_data.get('competitors', []))}")

        return enriched_context

    def format_research_summary(self, research_data: Dict) -> str:
        """Format research data as readable summary"""

        summary_parts = []

        if "product" in research_data:
            product = research_data["product"]
            summary_parts.append(f"📦 PRODUIT: {product.get('name')}")
            summary_parts.append(f"   Prix marché: {product.get('typical_pricing')}")
            summary_parts.append(f"   Concurrents: {', '.join(product.get('competitors', []))}")
            summary_parts.append(f"   Position: {product.get('market_position')}")

        if "client" in research_data:
            client = research_data["client"]
            summary_parts.append(f"\n🏢 CLIENT: {client.get('name')}")
            summary_parts.append(f"   Taille: {client.get('company_size')}")
            summary_parts.append(f"   Secteur: {client.get('industry')}")
            summary_parts.append(f"   Budget estimé: {client.get('budget_range')}")

        return "\n".join(summary_parts)

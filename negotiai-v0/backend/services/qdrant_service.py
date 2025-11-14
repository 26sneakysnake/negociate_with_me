# backend/services/qdrant_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from backend.config import get_settings
from typing import List, Dict
import json
import uuid

class QdrantService:
    def __init__(self):
        settings = get_settings()
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = settings.QDRANT_COLLECTION
        self.vector_size = settings.VECTOR_SIZE

    async def initialize_collection(self):
        """Create collection if not exists"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    async def load_tactics_database(self, tactics_file: str):
        """Load negotiation tactics from JSON file"""
        with open(tactics_file, 'r', encoding='utf-8') as f:
            tactics = json.load(f)

        # Import here to avoid circular dependency
        from backend.services.mistral_service import MistralService
        mistral = MistralService()

        points = []
        for tactic in tactics["tactics"]:
            # Embed tactic description
            vector = mistral.embed_text(
                f"{tactic['name']}: {tactic['description']}"
            )

            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "name": tactic["name"],
                    "category": tactic["category"],
                    "description": tactic["description"],
                    "example": tactic.get("example", ""),
                    "counter": tactic.get("counter", "")
                }
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return len(points)

    async def search_relevant_tactics(
        self,
        query_vector: List[float],
        limit: int = 10
    ) -> List[str]:
        """Search for relevant tactics"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        tactics = []
        for result in results:
            payload = result.payload
            tactic_text = f"{payload['name']} ({payload['category']}): {payload['description']}"
            if payload.get('example'):
                tactic_text += f" Example: {payload['example']}"
            tactics.append(tactic_text)

        return tactics

"""
Azure AI Search knowledge base service.
Implements hybrid search (vector + keyword) against the populated search index.
"""

import asyncio
import logging
import time
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI

from app.models.enums import Department
from app.models.schemas import KnowledgeArticle
from app.services.interfaces import KnowledgeServiceInterface

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "text-embedding-ada-002"


class AzureSearchKnowledgeService(KnowledgeServiceInterface):
    """Azure AI Search implementation with hybrid vector + keyword search."""

    def __init__(
        self,
        search_endpoint: str,
        search_key: str,
        index_name: str,
        openai_endpoint: str,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self._search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key),
        )

        # Use API key if provided, otherwise managed identity
        if openai_api_key:
            self._openai = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                api_key=openai_api_key,
                api_version="2024-02-15-preview",
            )
        else:
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            self._openai = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                azure_ad_token_provider=token_provider,
                api_version="2024-02-15-preview",
            )

        self._index_name = index_name
        logger.info("AzureSearchKnowledgeService initialized (index=%s)", index_name)

    def _get_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for query text."""
        response = self._openai.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text[:8000],
        )
        return response.data[0].embedding

    def _build_filter(self, department: Optional[Department]) -> Optional[str]:
        """Build OData filter for department.
        Currently disabled: index department values don't match enum values.
        Keyword + vector relevance provides sufficient filtering."""
        return None

    async def search(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> list[KnowledgeArticle]:
        """Hybrid search returning article metadata."""
        articles, _ = await self.search_with_content(query, department, limit)
        return articles

    async def search_with_content(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> tuple[list[KnowledgeArticle], list[dict]]:
        """Hybrid search returning both metadata and full content.
        Falls back to keyword-only search if embedding generation fails."""
        try:
            filter_expr = self._build_filter(department)

            # Try hybrid search with embeddings first
            vector_queries = []
            try:
                embedding = await asyncio.to_thread(self._get_embedding, query)
                vector_queries = [
                    VectorizedQuery(
                        vector=embedding,
                        k_nearest_neighbors=limit * 3,
                        fields="content_vector",
                    )
                ]
            except Exception as embed_err:
                logger.warning("Embedding failed, falling back to keyword search: %s", embed_err)

            # Execute search (hybrid if embedding succeeded, keyword-only otherwise)
            results = await asyncio.to_thread(
                lambda: list(
                    self._search_client.search(
                        search_text=query,
                        vector_queries=vector_queries if vector_queries else None,
                        filter=filter_expr,
                        select=["id", "title", "content", "snippet", "department", "category", "tags"],
                        top=limit,
                    )
                )
            )

            articles = []
            contents = []
            for result in results:
                score = result.get("@search.score", 0.0)
                dept_val = result.get("department")

                # Gracefully handle department values that don't match the enum
                dept = None
                if dept_val:
                    try:
                        dept = Department(dept_val)
                    except ValueError:
                        pass

                articles.append(
                    KnowledgeArticle(
                        article_id=result["id"],
                        title=result.get("title", ""),
                        url="",
                        snippet=result.get("snippet"),
                        relevance_score=min(1.0, score / 10.0),
                        department=dept,
                    )
                )
                contents.append({
                    "article_id": result["id"],
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "snippet": result.get("snippet", ""),
                    "tags": result.get("tags", []),
                })

            logger.info("Search '%s' returned %d results", query[:50], len(articles))
            return articles, contents

        except Exception as e:
            logger.error("Search failed: %s", e)
            return [], []

    async def get_article(
        self,
        article_id: str,
    ) -> Optional[KnowledgeArticle]:
        """Get a specific article by ID."""
        try:
            result = await asyncio.to_thread(
                self._search_client.get_document, key=article_id
            )
            if result:
                dept_val = result.get("department")
                dept = None
                if dept_val:
                    try:
                        dept = Department(dept_val)
                    except ValueError:
                        pass
                return KnowledgeArticle(
                    article_id=result["id"],
                    title=result.get("title", ""),
                    url="",
                    snippet=result.get("snippet"),
                    relevance_score=1.0,
                    department=dept,
                )
        except Exception as e:
            logger.error("Get article %s failed: %s", article_id, e)
        return None

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Check search service health by counting documents."""
        try:
            start = time.monotonic()
            count = await asyncio.to_thread(self._search_client.get_document_count)
            latency = int((time.monotonic() - start) * 1000)
            if count == 0:
                return False, latency, "Index is empty"
            return True, latency, None
        except Exception as e:
            return False, None, str(e)

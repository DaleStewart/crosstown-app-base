"""
Search Tool for RAG Pipeline - Lab 04 Solution

This module implements a hybrid search tool that combines vector (semantic) search
with traditional keyword search using Azure AI Search. Hybrid search provides
better recall than either approach alone.

Key Concepts:
- Vector search: Uses embeddings to find semantically similar content
- Keyword search: Traditional BM25-based text matching
- Hybrid search: Combines both approaches using Reciprocal Rank Fusion (RRF)
"""

import os
from dataclasses import dataclass
from typing import Optional

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI


@dataclass
class SearchResult:
    """
    Represents a single search result from Azure AI Search.

    Attributes:
        content: The text content of the document chunk
        score: Relevance score (higher is better, combines vector + keyword scores)
        metadata: Additional document information (source, page number, etc.)
    """
    content: str
    score: float
    metadata: dict


class SearchTool:
    """
    Hybrid search tool combining vector and keyword search capabilities.

    This class wraps Azure AI Search to provide:
    1. Vector search using embeddings from Azure OpenAI
    2. Keyword search using BM25 algorithm
    3. Hybrid search combining both for optimal results

    The hybrid approach typically outperforms either method alone because:
    - Vector search captures semantic meaning ("car" matches "automobile")
    - Keyword search catches exact terms and proper nouns
    - Combined ranking (RRF) balances both signals
    """

    def __init__(
        self,
        search_endpoint: Optional[str] = None,
        search_key: Optional[str] = None,
        index_name: Optional[str] = None,
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
        embedding_deployment: Optional[str] = None,
    ):
        """
        Initialize the search tool with Azure AI Search and OpenAI clients.

        Args:
            search_endpoint: Azure AI Search service URL
            search_key: Azure AI Search API key
            index_name: Name of the search index to query
            openai_endpoint: Azure OpenAI service URL
            openai_key: Azure OpenAI API key
            embedding_deployment: Name of the embedding model deployment

        Note: All parameters default to environment variables if not provided.
        This follows the 12-factor app pattern for configuration.
        """
        # Load configuration from environment variables as fallback
        # This allows flexible deployment without code changes
        self.search_endpoint = search_endpoint or os.environ["AZURE_SEARCH_ENDPOINT"]
        self.search_key = search_key or os.environ["AZURE_SEARCH_KEY"]
        self.index_name = index_name or os.environ["AZURE_SEARCH_INDEX"]
        self.openai_endpoint = openai_endpoint or os.environ["AZURE_OPENAI_ENDPOINT"]
        self.openai_key = openai_key or os.environ["AZURE_OPENAI_KEY"]
        self.embedding_deployment = embedding_deployment or os.environ.get(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"
        )

        # Initialize the Azure AI Search client
        # The SearchClient handles connection pooling and retries automatically
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.search_key),
        )

        # Initialize Azure OpenAI client for generating embeddings
        # We need embeddings to convert query text into vectors for semantic search
        self.openai_client = AzureOpenAI(
            azure_endpoint=self.openai_endpoint,
            api_key=self.openai_key,
            api_version="2025-01-01-preview",  # Use a recent stable API version
        )

    def _get_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding vector for the given text.

        Embeddings are dense vector representations that capture semantic meaning.
        Similar concepts will have similar vectors (measured by cosine similarity).

        Args:
            text: The text to embed (typically the user's query)

        Returns:
            A list of floats representing the embedding vector
            (typically 1536 dimensions for text-embedding-3-small)
        """
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_deployment,
        )
        # The API returns a list of embeddings; we only sent one text, so take the first
        return response.data[0].embedding

    def search(
        self,
        query: str,
        top_k: int = 5,
        vector_field: str = "content_vector",
        content_field: str = "content",
        use_hybrid: bool = True,
    ) -> list[SearchResult]:
        """
        Perform hybrid search combining vector and keyword search.

        The search process:
        1. Generate embedding for the query text
        2. Send both text query and vector to Azure AI Search
        3. Azure combines results using Reciprocal Rank Fusion (RRF)
        4. Return top-k results sorted by combined score

        Args:
            query: The user's search query in natural language
            top_k: Maximum number of results to return (default: 5)
            vector_field: Name of the field containing document vectors
            content_field: Name of the field containing document text
            use_hybrid: If True, use hybrid search; if False, vector-only

        Returns:
            List of SearchResult objects sorted by relevance score

        Raises:
            azure.core.exceptions.HttpResponseError: If search service fails
            openai.APIError: If embedding generation fails
        """
        try:
            # Step 1: Generate embedding for semantic/vector search
            # This converts the query into the same vector space as our indexed documents
            query_embedding = self._get_embedding(query)

            # Step 2: Create a VectorizedQuery for the vector search component
            # k_nearest_neighbors controls how many candidates are retrieved before fusion
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k * 2,  # Retrieve extra for better fusion results
                fields=vector_field,
            )

            # Step 3: Execute the search
            # When search_text is provided alongside vector_queries, Azure performs hybrid search
            if use_hybrid:
                # Hybrid search: combines vector similarity with BM25 keyword matching
                results = self.search_client.search(
                    search_text=query,  # Enables keyword search component
                    vector_queries=[vector_query],  # Enables vector search component
                    select=["id", "title", "content", "snippet", "department", "category"],
                    top=top_k,
                )
            else:
                # Vector-only search: useful when exact keyword matches aren't important
                results = self.search_client.search(
                    search_text=None,
                    vector_queries=[vector_query],
                    select=["id", "title", "content", "snippet", "department", "category"],
                    top=top_k,
                )

            # Step 4: Convert Azure results to our SearchResult dataclass
            search_results = []
            for result in results:
                # Extract the content and score
                content = result.get(content_field, "")
                score = result.get("@search.score", 0.0)

                # Build metadata from remaining fields
                # Exclude internal fields and the content we already extracted
                metadata = {
                    key: value
                    for key, value in result.items()
                    if not key.startswith("@") and key != content_field and key != vector_field
                }

                search_results.append(
                    SearchResult(
                        content=content,
                        score=score,
                        metadata=metadata,
                    )
                )

            return search_results

        except Exception as e:
            # In production, you'd want more specific exception handling
            # and proper logging. For the lab, we re-raise with context.
            raise RuntimeError(f"Search failed for query '{query}': {e}") from e

    def search_with_filter(
        self,
        query: str,
        filter_expression: str,
        top_k: int = 5,
        vector_field: str = "content_vector",
        content_field: str = "content",
    ) -> list[SearchResult]:
        """
        Perform hybrid search with an OData filter expression.

        Filters are useful for:
        - Restricting results to specific document sources
        - Date range filtering
        - Category/tag-based filtering
        - Multi-tenant isolation

        Args:
            query: The user's search query
            filter_expression: OData filter (e.g., "source eq 'manual.pdf'")
            top_k: Maximum results to return
            vector_field: Field containing document vectors
            content_field: Field containing document text

        Returns:
            Filtered list of SearchResult objects

        Example:
            results = tool.search_with_filter(
                query="installation steps",
                filter_expression="category eq 'setup' and version gt 2.0"
            )
        """
        try:
            query_embedding = self._get_embedding(query)

            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k * 2,
                fields=vector_field,
            )

            # The filter parameter applies OData filter syntax
            # Filters are applied BEFORE ranking, improving performance
            results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                filter=filter_expression,
                select=["id", "title", "content", "snippet", "department", "category"],
                top=top_k,
            )

            search_results = []
            for result in results:
                content = result.get(content_field, "")
                score = result.get("@search.score", 0.0)
                metadata = {
                    key: value
                    for key, value in result.items()
                    if not key.startswith("@") and key != content_field and key != vector_field
                }
                search_results.append(
                    SearchResult(content=content, score=score, metadata=metadata)
                )

            return search_results

        except Exception as e:
            raise RuntimeError(f"Filtered search failed: {e}") from e

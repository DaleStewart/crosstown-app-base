"""
Lab 04 - Index Setup Script
Creates the Azure AI Search index and indexes KB articles with embeddings.
"""

import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from openai import AzureOpenAI

# Configuration from environment
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "university-kb")

OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

def create_index(index_client: SearchIndexClient) -> None:
    """Create the search index with vector and semantic search support."""

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="url", type=SearchFieldDataType.String),
        SimpleField(name="snippet", type=SearchFieldDataType.String),
        SimpleField(name="department", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchField(
            name="tags",
            type=SearchFieldDataType.Collection(SearchFieldDataType.String),
            filterable=True,
        ),
        SimpleField(name="last_updated", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="my-vector-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="my-hnsw"),
        ],
        profiles=[
            VectorSearchProfile(
                name="my-vector-profile",
                algorithm_configuration_name="my-hnsw",
            ),
        ],
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")],
            title_field=SemanticField(field_name="title"),
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    print(f"Creating index '{INDEX_NAME}'...")
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' created successfully!")


def load_kb_articles(data_dir: Path) -> list[dict]:
    """Load all KB articles from JSON files."""
    articles = []
    for file_path in data_dir.glob("*.json"):
        with open(file_path) as f:
            data = json.load(f)
            if isinstance(data, list):
                articles.extend(data)
            else:
                articles.append(data)
    print(f"Loaded {len(articles)} articles from {data_dir}")
    return articles


def generate_embedding(text: str, client: AzureOpenAI) -> list[float]:
    """Generate embedding for text using Azure OpenAI."""
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text[:8000]  # Truncate to avoid token limits
    )
    return response.data[0].embedding


def index_documents(articles: list[dict], search_client: SearchClient, openai_client: AzureOpenAI) -> None:
    """Index KB articles with embeddings."""
    documents = []

    for i, article in enumerate(articles):
        print(f"Processing {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")

        # Generate embedding for content
        content = article.get("content", "")
        embedding = generate_embedding(content, openai_client)

        doc = {
            "id": article.get("article_id", f"kb-{i}"),
            "title": article.get("title", ""),
            "content": content,
            "url": article.get("url", ""),
            "snippet": article.get("snippet", ""),
            "department": article.get("department", ""),
            "category": article.get("category", ""),
            "tags": article.get("tags", []),
            "last_updated": article.get("last_updated", ""),
            "content_vector": embedding,
        }
        documents.append(doc)

    # Upload in batches
    print(f"\nUploading {len(documents)} documents to index...")
    result = search_client.upload_documents(documents)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Successfully indexed {succeeded}/{len(documents)} documents!")


def main():
    print("=" * 60)
    print("Lab 04 - Azure AI Search Index Setup")
    print("=" * 60)

    # Initialize clients
    credential = AzureKeyCredential(SEARCH_KEY)
    index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=credential)
    search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=credential)
    openai_client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview"
    )

    # Step 1: Create index
    create_index(index_client)

    # Step 2: Load KB articles
    data_dir = Path(__file__).parent / "data"
    articles = load_kb_articles(data_dir)

    # Step 3: Index documents with embeddings
    index_documents(articles, search_client, openai_client)

    print("\n" + "=" * 60)
    print("Index setup complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

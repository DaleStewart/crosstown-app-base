# Lab 04 - Build RAG Pipeline: Completion Specification

## What "Done" Looks Like

Lab 04 is complete when you have built a working RAG (Retrieval-Augmented Generation) pipeline that retrieves relevant knowledge base articles using hybrid search and generates responses with proper source citations. You should be able to:

1. Configure and create an Azure AI Search index with both vector and keyword search capabilities
2. Index knowledge base articles with embeddings for semantic search
3. Implement hybrid search that combines vector similarity and keyword matching
4. Build a RetrieveAgent that generates grounded responses with inline citations

A successfully completed Lab 04 means you have a functional RAG system that can answer questions based on your knowledge base with proper attribution, ready to be integrated into a larger agent architecture.

---

## Checkable Deliverables

### 1. Hybrid Search Returns Relevant KB Articles

**What it verifies:**
- Azure AI Search index is properly configured with vector and keyword fields
- Embeddings are correctly generated and indexed
- Hybrid search combines both search strategies effectively
- Results are relevant to the query and properly ranked

**Acceptance Criteria:**
- [ ] Azure AI Search index exists with all required fields (id, title, content, contentVector, category, tags, lastUpdated)
- [ ] Vector field is configured with correct dimensions (1536 for text-embedding-3-small)
- [ ] All KB articles are indexed with their embeddings
- [ ] Hybrid search returns top-k relevant documents for test queries
- [ ] Search results include relevance scores
- [ ] Search completes within 2 seconds for typical queries
- [ ] Category filtering works correctly when specified

**How to Test:**

```bash
# Verify index exists and has documents
az search index show --service-name <your-service> --name kb-index

# Check document count
az search document search --service-name <your-service> \
    --index-name kb-index --search "*" --count

# Test hybrid search with a sample query
python -m pytest tests/test_search.py -v
```

**Test Cases:**

| Query | Expected Behavior |
|-------|-------------------|
| "How do I reset my password?" | Returns password-related KB articles |
| "vacation policy" | Returns HR/policy articles about PTO |
| "Error code E-1234" | Finds exact match even if semantically unrelated |
| "working from home guidelines" | Returns remote work articles (semantic match) |
| "asdfghjkl" (gibberish) | Returns empty or low-confidence results |

**Verification Script:**

```python
# test_search.py
import pytest
from search_tool import hybrid_search

@pytest.mark.asyncio
async def test_hybrid_search_returns_results():
    """Verify hybrid search returns relevant results."""
    results = await hybrid_search("password reset", top_k=5)

    assert len(results) > 0, "Search should return results"
    assert results[0]["score"] > 0.5, "Top result should have good relevance"
    assert "password" in results[0]["content"].lower() or \
           "password" in results[0]["title"].lower(), \
           "Top result should be about passwords"

@pytest.mark.asyncio
async def test_hybrid_search_with_filter():
    """Verify category filtering works."""
    results = await hybrid_search(
        "policy",
        top_k=5,
        filter_category="HR"
    )

    for result in results:
        assert result["category"] == "HR", \
            "All results should be in HR category"

@pytest.mark.asyncio
async def test_vector_search_semantic_matching():
    """Verify vector search finds semantically similar content."""
    # Search for synonym - "WFH" should find "remote work"
    results = await hybrid_search("WFH guidelines", top_k=5)

    titles = [r["title"].lower() for r in results]
    assert any("remote" in t or "home" in t for t in titles), \
        "Should find remote work articles for WFH query"
```

---

### 2. Citations Included in Responses

**What it verifies:**
- RetrieveAgent correctly builds context from retrieved documents
- Generated responses include inline citations [1], [2], etc.
- Source list is included at the end of responses
- Citations correspond to actually retrieved documents
- Responses are grounded in the knowledge base (no hallucination)

**Acceptance Criteria:**
- [ ] Responses include inline citations in [N] format
- [ ] A "Sources:" section lists all cited documents
- [ ] Each citation corresponds to a retrieved document
- [ ] Citations are accurate (referenced content exists in cited source)
- [ ] Responses clearly indicate when information is not found
- [ ] No fabricated citations or sources
- [ ] At least 90% of answers include at least one citation

**How to Test:**

```bash
# Run citation tests
python -m pytest tests/test_citations.py -v
```

**Expected Response Format:**

```
Query: How do I reset my password?

Response:
To reset your password, navigate to the login page and click "Forgot Password" [1].
You will receive an email with a reset link that expires in 24 hours [1].
For security reasons, your new password must be at least 12 characters and include
a number and special character [2].

Sources:
[1] Password Reset Procedure (kb-001)
[2] Password Security Requirements (kb-015)
```

**Test Cases:**

| Scenario | Expected Citation Behavior |
|----------|---------------------------|
| Direct match query | Multiple relevant citations |
| Partial match query | Citations for relevant parts, acknowledgment of gaps |
| No match query | Clear statement that information not found, no citations |
| Multi-topic query | Citations from multiple documents |

**Verification Script:**

```python
# test_citations.py
import pytest
import re
from retrieve_agent import RetrieveAgent

@pytest.mark.asyncio
async def test_response_includes_citations():
    """Verify responses include inline citations."""
    agent = RetrieveAgent(...)  # Initialize
    response = await agent.answer("How do I reset my password?")

    # Check for inline citations [1], [2], etc.
    citation_pattern = r'\[\d+\]'
    citations = re.findall(citation_pattern, response.answer)

    assert len(citations) > 0, "Response should include at least one citation"

@pytest.mark.asyncio
async def test_sources_list_present():
    """Verify sources list is included."""
    agent = RetrieveAgent(...)
    response = await agent.answer("What is the vacation policy?")

    assert len(response.sources) > 0, "Response should include sources"
    assert all("id" in s and "title" in s for s in response.sources), \
        "Each source should have id and title"

@pytest.mark.asyncio
async def test_citations_match_sources():
    """Verify inline citations correspond to sources list."""
    agent = RetrieveAgent(...)
    response = await agent.answer("How do I submit expenses?")

    # Extract citation numbers from answer
    citation_numbers = set(
        int(n) for n in re.findall(r'\[(\d+)\]', response.answer)
    )

    # Verify all citations have corresponding sources
    assert max(citation_numbers) <= len(response.sources), \
        "All citations should have corresponding sources"

@pytest.mark.asyncio
async def test_no_hallucinated_citations():
    """Verify citations reference actual content."""
    agent = RetrieveAgent(...)
    response = await agent.answer("password requirements")

    # For each citation, verify the claim appears in the source
    # This is a simplified check - production would be more thorough
    assert "Sources:" in response.answer or len(response.sources) > 0, \
        "Response should have traceable sources"

@pytest.mark.asyncio
async def test_handles_no_results_gracefully():
    """Verify agent handles queries with no KB matches."""
    agent = RetrieveAgent(...)
    response = await agent.answer("quantum entanglement in black holes")

    # Should acknowledge lack of information, not fabricate
    answer_lower = response.answer.lower()
    assert any(phrase in answer_lower for phrase in [
        "don't have information",
        "no relevant",
        "not found",
        "cannot find",
        "knowledge base does not contain"
    ]), "Should acknowledge when information is not available"
```

---

## Verification Steps

### Step 1: Index Verification

```bash
# 1. Verify Azure AI Search index exists
az search index show --service-name <service> --name kb-index --query "name"

# 2. Check field configuration
az search index show --service-name <service> --name kb-index --query "fields[].{name:name, type:type}"

# 3. Verify document count matches KB articles
az search document search --service-name <service> \
    --index-name kb-index --search "*" --count

# Expected: Document count matches number of KB articles in data/ directory
```

### Step 2: Search Quality Verification

```bash
# Run the search test suite
python -m pytest tests/test_search.py -v --tb=short

# Expected output:
# test_search.py::test_hybrid_search_returns_results PASSED
# test_search.py::test_hybrid_search_with_filter PASSED
# test_search.py::test_vector_search_semantic_matching PASSED
# test_search.py::test_keyword_search_exact_match PASSED
# test_search.py::test_search_performance PASSED
```

### Step 3: RAG Pipeline End-to-End Test

```python
# Run interactive test
python test_rag.py

# Sample interaction:
# Query: How do I reset my password?
# --------------------------------------------------
# Answer: To reset your password, go to the login page and click
# "Forgot Password" [1]. Enter your email address and you'll receive
# a reset link within 5 minutes [1]. The link expires after 24 hours [2].
#
# Sources:
#   - [kb-001] Password Reset Procedure
#   - [kb-002] Account Security FAQ
```

### Step 4: Citation Accuracy Verification

```bash
# Run citation tests
python -m pytest tests/test_citations.py -v

# Manual verification:
# 1. Run a query
# 2. Note the citations [1], [2], etc.
# 3. Read the corresponding source documents
# 4. Verify the cited claims appear in those documents
```

---

## Assessment Rubric

### Total Points: 25 (RAG Pipeline)

| Criteria | Points | Description |
|----------|--------|-------------|
| **Index Configuration** | 5 | Azure AI Search index correctly configured with vector and keyword fields |
| **Embedding Generation** | 4 | KB articles indexed with proper embeddings |
| **Hybrid Search Implementation** | 6 | Search combines vector and keyword strategies effectively |
| **Citation Quality** | 6 | Responses include accurate, verifiable citations |
| **Error Handling** | 4 | Graceful handling of edge cases and failures |

### Detailed Scoring Guide

#### Index Configuration (5 points)
- **5 points:** Index has all fields, correct types, vector dimensions match, semantic config enabled
- **4 points:** Index works but missing optional optimizations (e.g., no semantic ranking)
- **3 points:** Index created but vector search not properly configured
- **2 points:** Index exists but significant configuration issues
- **0-1 points:** Index not created or fundamentally broken

#### Embedding Generation (4 points)
- **4 points:** All articles indexed, correct embedding dimensions, batch processing, retry logic
- **3 points:** All articles indexed but no optimization (slow, no retries)
- **2 points:** Most articles indexed but some failures
- **1 point:** Few articles indexed, many failures
- **0 points:** No embeddings generated

#### Hybrid Search Implementation (6 points)
- **6 points:** Combines vector + keyword, proper relevance scoring, filtering works, fast performance
- **5 points:** Hybrid search works but minor issues (e.g., slow, no filtering)
- **4 points:** Both search types work but not properly combined
- **3 points:** Only one search type works (vector OR keyword)
- **2 points:** Search returns results but poor relevance
- **0-1 points:** Search not functional

#### Citation Quality (6 points)
- **6 points:** All responses cited, citations accurate, sources listed, handles no-match gracefully
- **5 points:** Citations present but occasional accuracy issues
- **4 points:** Citations present but frequently missing or inaccurate
- **3 points:** Some citations but inconsistent format
- **2 points:** Rarely includes citations
- **0-1 points:** No citations or fabricated citations

#### Error Handling (4 points)
- **4 points:** Handles API errors, empty results, rate limits, timeout gracefully
- **3 points:** Most error cases handled
- **2 points:** Some error handling but crashes on edge cases
- **1 point:** Minimal error handling
- **0 points:** No error handling, crashes frequently

---

## Common Failure Modes and Resolutions

### Index Creation Fails

**Symptom:** `az search index create` returns error

**Resolution:**
```bash
# Check service tier supports vector search
az search service show --name <service> --query "sku.name"
# Vector search requires Basic tier or higher

# Verify field definitions
cat index_schema.json | jq '.fields[] | select(.type == "Collection(Edm.Single)")'

# Check dimensions match embedding model
# text-embedding-3-small = 1536 dimensions
# text-embedding-3-small = 1536 dimensions
# text-embedding-3-large = 3072 dimensions
```

---

### Embeddings Have Wrong Dimensions

**Symptom:** Index upload fails with dimension mismatch error

**Resolution:**
```python
# Verify embedding dimensions
embedding = await generate_embedding("test", client)
print(f"Embedding dimensions: {len(embedding)}")

# Update index schema to match
# dimensions: 1536  # for ada-002
# dimensions: 3072  # for text-embedding-3-large
```

---

### Search Returns Irrelevant Results

**Symptom:** Top results don't match query intent

**Resolution:**
1. Verify hybrid search is using both vector AND keyword
2. Check if semantic ranking is enabled
3. Review the embedding model - try a newer version
4. Ensure content field contains meaningful text

```python
# Debug search scores
results = search_client.search(
    search_text=query,
    vector_queries=[vector_query],
    include_total_count=True,
    select=["id", "title", "@search.score", "@search.reranker_score"]
)
for r in results:
    print(f"{r['title']}: score={r['@search.score']}, rerank={r.get('@search.reranker_score')}")
```

---

### Citations Missing or Incorrect

**Symptom:** Responses don't include [1], [2] citations or cite wrong sources

**Resolution:**
```python
# Verify system prompt instructs citation format
system_prompt = """
IMPORTANT: Always cite sources using [1], [2] format.
Include a Sources: section at the end listing all cited documents.
"""

# Verify context includes document identifiers
def _build_context(self, documents):
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(
            f"[Source {i}] Title: {doc['title']}\n"
            f"Content: {doc['content']}\n"
        )
    return "\n---\n".join(context_parts)

# Use lower temperature for more consistent citation behavior
response = await client.chat.completions.create(
    model=deployment,
    messages=messages,
    temperature=0.3  # Lower = more deterministic
)
```

---

### Rate Limiting During Indexing

**Symptom:** `RateLimitError` when generating embeddings

**Resolution:**
```python
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(multiplier=1, min=4, max=60), stop=stop_after_attempt(5))
async def generate_embedding_with_retry(text: str, client) -> list[float]:
    """Generate embedding with automatic retry on rate limit."""
    return await generate_embedding(text, client)

# Process in smaller batches
BATCH_SIZE = 10
for i in range(0, len(articles), BATCH_SIZE):
    batch = articles[i:i+BATCH_SIZE]
    await asyncio.gather(*[process_article(a) for a in batch])
    await asyncio.sleep(1)  # Rate limit buffer
```

---

## Success Checklist

Before proceeding to Lab 05, ensure all items are checked:

- [ ] Azure AI Search index created with vector and keyword fields
- [ ] All KB articles indexed with embeddings
- [ ] `hybrid_search()` function returns relevant results
- [ ] Search combines vector similarity and keyword matching
- [ ] Category filtering works correctly
- [ ] `RetrieveAgent.answer()` generates responses with citations
- [ ] Inline citations [1], [2] appear in responses
- [ ] Sources list included with document titles and IDs
- [ ] Citations are accurate (reference actual source content)
- [ ] Agent handles "no results" queries gracefully
- [ ] All test cases pass
- [ ] Error handling covers common failure modes

**Estimated Time:** 2-3 hours

**Points Possible:** 25 (RAG Pipeline)

**Prerequisites:**
- Lab 01 completed (understanding of agent patterns)
- Lab 02 completed (Azure MCP and AI services configured)
- Azure AI Search service deployed (Basic tier or higher)
- Azure OpenAI with embedding model deployed

**Next Step:** Proceed to Lab 05 - Agent Orchestration

"""
Lab 05 - Agent Orchestration Test Script
Tests the three-agent pipeline: QueryAgent → RouterAgent → ActionAgent
"""

import asyncio
import sys
import os
import pytest

# Add start directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "start"))

from openai import AzureOpenAI

# Configuration
OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
OPENAI_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_KEY")
INDEX_NAME = os.environ.get("AZURE_SEARCH_INDEX_NAME", "university-kb")

requires_azure = pytest.mark.skipif(
    not OPENAI_ENDPOINT or not OPENAI_KEY,
    reason="Azure OpenAI credentials not configured"
)


@requires_azure
@pytest.mark.asyncio
async def test_query_agent():
    """Test QueryAgent intent classification."""
    print("\n" + "=" * 60)
    print("TEST 1: QueryAgent - Intent Classification")
    print("=" * 60)

    from query_agent import QueryAgent

    client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview",
    )

    agent = QueryAgent(client, "gpt-4o")

    test_cases = [
        ("How do I reset my password?", "knowledge_query"),
        ("Hello!", "greeting"),
        ("I want to speak to a human", "escalation"),
        ("What's the status of ticket TKT-12345?", "ticket_status"),
    ]

    for message, expected_intent in test_cases:
        result = await agent.analyze(message)
        status = (
            "✅"
            if expected_intent in result.intent.value.lower()
            or result.intent.value.lower() in expected_intent
            else "⚠️"
        )
        print(f"{status} '{message[:40]}...'")
        print(f"   Intent: {result.intent.value} (expected: {expected_intent})")
        print(f"   Confidence: {result.confidence:.2f}")
        print()


@requires_azure
@pytest.mark.asyncio
async def test_router_agent():
    """Test RouterAgent routing decisions."""
    print("\n" + "=" * 60)
    print("TEST 2: RouterAgent - Routing Decisions")
    print("=" * 60)

    from query_agent import QueryAgent, QueryResult, Intent
    from router_agent import RouterAgent

    client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview",
    )

    router = RouterAgent(client, "gpt-4o")

    # Create mock query results
    test_queries = [
        QueryResult(
            original_query="How do I connect to WiFi?",
            intent=Intent.KNOWLEDGE_QUERY,
            confidence=0.95,
            entities=[],
            requires_clarification=False,
        ),
        QueryResult(
            original_query="I need help NOW!",
            intent=Intent.ESCALATION,
            confidence=0.90,
            entities=[],
            requires_clarification=False,
        ),
    ]

    for query in test_queries:
        decision = await router.route(query)
        print(f"Query: '{query.original_query}'")
        print(f"   Intent: {query.intent.value}")
        print(f"   Routed to: {decision.target_agent}")
        print(f"   Reasoning: {decision.reasoning[:60]}...")
        print()


@requires_azure
@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete pipeline with multi-turn conversation."""
    print("\n" + "=" * 60)
    print("TEST 3: Full Pipeline - Multi-Turn Conversation")
    print("=" * 60)

    from pipeline import AgentPipeline

    client = AzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version="2024-02-15-preview",
    )

    pipeline = AgentPipeline(
        openai_client=client,
        model_deployment="gpt-4o",
    )

    # Multi-turn conversation
    conversation = [
        "Hi there!",
        "How do I reset my university password?",
        "What if the self-service portal doesn't work?",
        "Thanks, that helps!",
    ]

    session_id = None

    for i, message in enumerate(conversation, 1):
        print(f"\n--- Turn {i} ---")
        print(f"User: {message}")

        result, session_id = await pipeline.process(message, session_id)

        print(f"Agent: {result.content[:200]}...")
        print(f"Confidence: {result.confidence:.2f}")
        if result.sources:
            print(
                f"Sources: {[s.get('title', s.get('id', 'unknown'))[:30] for s in result.sources[:2]]}"
            )

    print(
        f"\n✅ Session maintained across {len(conversation)} turns (ID: {session_id[:8]}...)"
    )


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Lab 05 - Agent Orchestration Tests")
    print("=" * 60)

    try:
        # Test 1: QueryAgent
        await test_query_agent()

        # Test 2: RouterAgent
        await test_router_agent()

        # Test 3: Full Pipeline
        await test_full_pipeline()

        print("\n" + "=" * 60)
        print("✅ All Lab 05 tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

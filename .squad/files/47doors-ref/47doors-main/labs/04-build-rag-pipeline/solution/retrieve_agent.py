"""
Retrieve Agent for RAG Pipeline - Lab 04 Solution

This module implements a Retrieval-Augmented Generation (RAG) agent that:
1. Uses SearchTool to retrieve relevant documents
2. Builds context from search results
3. Sends context + query to Azure OpenAI for generation
4. Formats the response with proper citations

RAG Pattern Benefits:
- Grounds LLM responses in actual documents (reduces hallucination)
- Provides traceable citations for verification
- Allows the LLM to answer questions about private/recent data
"""

import os
from dataclasses import dataclass
from typing import Optional

from openai import AzureOpenAI

from search_tool import SearchResult, SearchTool


@dataclass
class RAGResponse:
    """
    Represents the complete response from the RAG pipeline.

    Attributes:
        answer: The generated answer with inline citations [1], [2], etc.
        sources: List of source documents used to generate the answer
        token_usage: Dictionary with prompt_tokens, completion_tokens, total_tokens
    """
    answer: str
    sources: list[SearchResult]
    token_usage: dict


class RetrieveAgent:
    """
    RAG Agent that retrieves relevant context and generates grounded responses.

    The RAG pipeline flow:
    1. User asks a question
    2. SearchTool finds relevant document chunks
    3. Agent builds a prompt with retrieved context
    4. Azure OpenAI generates an answer using only the provided context
    5. Response includes citations mapping to source documents

    This approach ensures:
    - Answers are grounded in actual documents
    - Users can verify claims by checking citations
    - The model doesn't rely solely on its training data
    """

    # System prompt instructs the LLM how to behave
    # Key elements: use only provided context, cite sources, admit uncertainty
    DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.

IMPORTANT INSTRUCTIONS:
1. Only use information from the provided context to answer questions
2. If the context doesn't contain enough information, say "I don't have enough information to answer this question"
3. Always cite your sources using [1], [2], etc. corresponding to the context chunks
4. Be concise but thorough in your answers
5. If multiple sources support a point, cite all of them

Context chunks are numbered [1], [2], [3], etc. Reference them in your answer."""

    def __init__(
        self,
        search_tool: Optional[SearchTool] = None,
        openai_endpoint: Optional[str] = None,
        openai_key: Optional[str] = None,
        chat_deployment: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the RAG agent with search and generation capabilities.

        Args:
            search_tool: Pre-configured SearchTool instance (created if not provided)
            openai_endpoint: Azure OpenAI service URL
            openai_key: Azure OpenAI API key
            chat_deployment: Name of the chat model deployment (e.g., gpt-4)
            system_prompt: Custom system prompt (uses DEFAULT_SYSTEM_PROMPT if not provided)
        """
        # Initialize search tool - either use provided or create new
        # Dependency injection makes testing easier
        self.search_tool = search_tool or SearchTool()

        # Load OpenAI configuration
        self.openai_endpoint = openai_endpoint or os.environ["AZURE_OPENAI_ENDPOINT"]
        self.openai_key = openai_key or os.environ["AZURE_OPENAI_KEY"]
        self.chat_deployment = chat_deployment or os.environ.get(
            "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"
        )

        # Initialize the Azure OpenAI client for chat completions
        self.openai_client = AzureOpenAI(
            azure_endpoint=self.openai_endpoint,
            api_key=self.openai_key,
            api_version="2025-01-01-preview",
        )

        # Store system prompt - this defines the agent's behavior
        self.system_prompt = system_prompt or self.DEFAULT_SYSTEM_PROMPT

    def _build_context(self, search_results: list[SearchResult]) -> str:
        """
        Build a formatted context string from search results.

        Each result is numbered [1], [2], etc. so the LLM can reference them.
        We include metadata (like source document) to help the model understand
        where information comes from.

        Args:
            search_results: List of SearchResult objects from the search tool

        Returns:
            Formatted string with numbered context chunks
        """
        if not search_results:
            return "No relevant context found."

        context_parts = []
        for i, result in enumerate(search_results, start=1):
            # Format each chunk with its number and metadata
            # The score helps us understand relevance (useful for debugging)
            source_info = result.metadata.get("source", "Unknown source")

            context_parts.append(
                f"[{i}] (Source: {source_info}, Relevance: {result.score:.3f})\n"
                f"{result.content}"
            )

        # Join with clear separators for readability
        return "\n\n---\n\n".join(context_parts)

    def _build_user_message(self, query: str, context: str) -> str:
        """
        Construct the user message containing context and query.

        The structure is important:
        1. Context comes first so the model "sees" it before the question
        2. Clear separation between context and question
        3. Explicit instruction to use citations

        Args:
            query: The user's original question
            context: Formatted context string from _build_context

        Returns:
            Complete user message for the chat API
        """
        return f"""## Retrieved Context

{context}

## Question

{query}

Please answer the question using only the information from the context above. Include citations [1], [2], etc. to indicate which sources support your answer."""

    def query(
        self,
        question: str,
        top_k: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        filter_expression: Optional[str] = None,
    ) -> RAGResponse:
        """
        Execute the full RAG pipeline: retrieve context and generate response.

        Pipeline steps:
        1. Search for relevant documents using hybrid search
        2. Build context from top-k results
        3. Construct prompt with context and question
        4. Call Azure OpenAI to generate answer
        5. Return answer with sources and usage stats

        Args:
            question: The user's question in natural language
            top_k: Number of search results to include in context
            temperature: LLM temperature (lower = more focused, higher = more creative)
            max_tokens: Maximum tokens in the generated response
            filter_expression: Optional OData filter for search

        Returns:
            RAGResponse containing answer, sources, and token usage

        Example:
            response = agent.query(
                question="What are the installation requirements?",
                top_k=5,
                temperature=0.3
            )
            print(response.answer)
            for i, source in enumerate(response.sources, 1):
                print(f"[{i}] {source.metadata.get('source')}")
        """
        # Step 1: Retrieve relevant documents
        # We use hybrid search for best results (vector + keyword)
        if filter_expression:
            search_results = self.search_tool.search_with_filter(
                query=question,
                filter_expression=filter_expression,
                top_k=top_k,
            )
        else:
            search_results = self.search_tool.search(
                query=question,
                top_k=top_k,
            )

        # Step 2: Build context from search results
        # This formats the results with numbers for citation
        context = self._build_context(search_results)

        # Step 3: Construct the messages for the chat API
        # The system message defines behavior, user message contains context + question
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self._build_user_message(question, context)},
        ]

        # Step 4: Call Azure OpenAI to generate the response
        # Temperature 0.3 is a good balance for factual Q&A (not too creative)
        response = self.openai_client.chat.completions.create(
            model=self.chat_deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Step 5: Extract the answer and usage statistics
        answer = response.choices[0].message.content
        token_usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        return RAGResponse(
            answer=answer,
            sources=search_results,
            token_usage=token_usage,
        )

    def query_with_history(
        self,
        question: str,
        conversation_history: list[dict],
        top_k: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1000,
    ) -> RAGResponse:
        """
        Execute RAG pipeline with conversation history for multi-turn chat.

        This method enables follow-up questions by including previous
        conversation turns. The search is still performed on the new question,
        but the LLM has context from previous exchanges.

        Args:
            question: The user's current question
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            top_k: Number of search results to include
            temperature: LLM temperature setting
            max_tokens: Maximum response tokens

        Returns:
            RAGResponse with answer, sources, and usage stats

        Note:
            For long conversations, consider summarizing history or
            using a sliding window to stay within token limits.
        """
        # Retrieve fresh context for the new question
        search_results = self.search_tool.search(query=question, top_k=top_k)
        context = self._build_context(search_results)

        # Build messages including conversation history
        # Structure: system -> history -> new user message with context
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        # This gives the model context about previous exchanges
        messages.extend(conversation_history)

        # Add current question with fresh context
        messages.append({
            "role": "user",
            "content": self._build_user_message(question, context),
        })

        # Generate response
        response = self.openai_client.chat.completions.create(
            model=self.chat_deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content
        token_usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

        return RAGResponse(
            answer=answer,
            sources=search_results,
            token_usage=token_usage,
        )

    def format_response_with_sources(self, rag_response: RAGResponse) -> str:
        """
        Format the RAG response into a human-readable string with source list.

        This helper method creates a nicely formatted output including:
        1. The generated answer
        2. A numbered list of sources with their metadata
        3. Token usage statistics (useful for monitoring costs)

        Args:
            rag_response: The RAGResponse from query() or query_with_history()

        Returns:
            Formatted string ready for display
        """
        # Start with the main answer
        output_parts = [
            "## Answer\n",
            rag_response.answer,
            "\n\n## Sources\n",
        ]

        # Add numbered source list
        for i, source in enumerate(rag_response.sources, start=1):
            source_name = source.metadata.get("source", "Unknown")
            # Truncate long content for display
            content_preview = source.content[:150] + "..." if len(source.content) > 150 else source.content
            output_parts.append(
                f"[{i}] **{source_name}** (score: {source.score:.3f})\n"
                f"    {content_preview}\n"
            )

        # Add token usage for cost monitoring
        output_parts.append(
            f"\n## Usage\n"
            f"Prompt tokens: {rag_response.token_usage['prompt_tokens']}\n"
            f"Completion tokens: {rag_response.token_usage['completion_tokens']}\n"
            f"Total tokens: {rag_response.token_usage['total_tokens']}"
        )

        return "\n".join(output_parts)


# Example usage (only runs if executed directly, not when imported)
if __name__ == "__main__":
    # This demonstrates how to use the RetrieveAgent
    # In production, you'd load environment variables from a .env file

    # Initialize the agent (uses environment variables by default)
    agent = RetrieveAgent()

    # Simple query
    question = "What are the system requirements for installation?"
    response = agent.query(question)

    # Print formatted response
    print(agent.format_response_with_sources(response))

    # Example with conversation history
    history = [
        {"role": "user", "content": "What is the product about?"},
        {"role": "assistant", "content": "Based on the documentation, the product is..."},
    ]
    follow_up = "How do I get started with it?"
    response = agent.query_with_history(follow_up, history)
    print(agent.format_response_with_sources(response))

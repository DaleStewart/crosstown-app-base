"""
Tests for Lab Solution Code

These tests validate that the solution code for Labs 04, 05, and 07
is syntactically correct and follows the expected patterns.

Participants can run these tests to verify their implementations:
    pytest tests/test_lab_solutions.py -v

Note: These tests use mocks and don't require Azure credentials.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch


# Add labs to path for imports
LABS_DIR = Path(__file__).parent.parent.parent / "labs"


class TestLab04SearchTool:
    """Tests for Lab 04 - Build RAG Pipeline solution code."""

    def test_search_tool_imports(self):
        """Test that search_tool.py can be parsed (syntax check)."""
        solution_path = LABS_DIR / "04-build-rag-pipeline" / "solution" / "search_tool.py"

        if not solution_path.exists():
            pytest.skip("Lab 04 solution not found")

        # Read and compile to check syntax
        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        # This will raise SyntaxError if code is invalid
        compile(code, str(solution_path), "exec")

    def test_search_tool_has_required_classes(self):
        """Test that search_tool.py defines expected classes."""
        solution_path = LABS_DIR / "04-build-rag-pipeline" / "solution" / "search_tool.py"

        if not solution_path.exists():
            pytest.skip("Lab 04 solution not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Check for expected class definitions
        assert "class SearchResult" in code, "SearchResult dataclass should be defined"
        assert "class SearchTool" in code, "SearchTool class should be defined"
        assert "def search(" in code, "search method should be defined"
        assert "_get_embedding" in code, "Embedding generation should be implemented"

    def test_retrieve_agent_imports(self):
        """Test that retrieve_agent.py can be parsed."""
        solution_path = LABS_DIR / "04-build-rag-pipeline" / "solution" / "retrieve_agent.py"

        if not solution_path.exists():
            pytest.skip("Lab 04 retrieve_agent not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

        # Check for RAG pattern implementation
        assert "class RetrieveAgent" in code or "def retrieve" in code, \
            "RetrieveAgent or retrieve function should be defined"


class TestLab05AgentOrchestration:
    """Tests for Lab 05 - Agent Orchestration solution code."""

    def test_query_agent_syntax(self):
        """Test query_agent.py syntax."""
        solution_path = LABS_DIR / "05-agent-orchestration" / "solution" / "query_agent.py"

        if not solution_path.exists():
            pytest.skip("Lab 05 query_agent not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

        # Check for expected patterns
        assert "class QueryAgent" in code, "QueryAgent class should be defined"
        assert "async def analyze" in code or "def analyze" in code, \
            "analyze method should be defined"

    def test_router_agent_syntax(self):
        """Test router_agent.py syntax."""
        solution_path = LABS_DIR / "05-agent-orchestration" / "solution" / "router_agent.py"

        if not solution_path.exists():
            pytest.skip("Lab 05 router_agent not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

        # Check for expected patterns
        assert "class RouterAgent" in code, "RouterAgent class should be defined"
        assert "route" in code, "route method should be defined"
        assert "RoutingDecision" in code, "RoutingDecision should be used"

    def test_action_agent_syntax(self):
        """Test action_agent.py syntax."""
        solution_path = LABS_DIR / "05-agent-orchestration" / "solution" / "action_agent.py"

        if not solution_path.exists():
            pytest.skip("Lab 05 action_agent not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

        # Check for expected patterns
        assert "ActionAgent" in code or "BaseActionAgent" in code, \
            "ActionAgent or BaseActionAgent should be defined"
        assert "execute" in code, "execute method should be defined"
        assert "ActionResult" in code, "ActionResult should be used"

    def test_pipeline_syntax(self):
        """Test pipeline.py syntax."""
        solution_path = LABS_DIR / "05-agent-orchestration" / "solution" / "pipeline.py"

        if not solution_path.exists():
            pytest.skip("Lab 05 pipeline not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

        # Check for expected patterns
        assert "class AgentPipeline" in code or "class Pipeline" in code, \
            "Pipeline class should be defined"
        assert "async def process" in code or "def process" in code, \
            "process method should be defined"
        assert "Session" in code, "Session management should be implemented"

    def test_pipeline_has_three_agents(self):
        """Test that pipeline wires up all three agents."""
        solution_path = LABS_DIR / "05-agent-orchestration" / "solution" / "pipeline.py"

        if not solution_path.exists():
            pytest.skip("Lab 05 pipeline not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        # All three agent types should be referenced
        assert "QueryAgent" in code, "Pipeline should use QueryAgent"
        assert "RouterAgent" in code, "Pipeline should use RouterAgent"
        assert "ActionAgent" in code or "action_agent" in code, \
            "Pipeline should use ActionAgent(s)"


class TestLab07MCPServer:
    """Tests for Lab 07 - MCP Server solution code."""

    def test_mcp_server_syntax(self):
        """Test mcp_server.py syntax."""
        solution_path = LABS_DIR / "07-mcp-server" / "solution" / "mcp_server.py"

        if not solution_path.exists():
            pytest.skip("Lab 07 mcp_server not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        compile(code, str(solution_path), "exec")

    def test_mcp_server_has_tools(self):
        """Test that MCP server defines tools."""
        solution_path = LABS_DIR / "07-mcp-server" / "solution" / "mcp_server.py"

        if not solution_path.exists():
            pytest.skip("Lab 07 mcp_server not found")

        with open(solution_path, "r", encoding="utf-8") as f:
            code = f.read()

        # MCP servers should define tools
        assert "tool" in code.lower() or "Tool" in code, \
            "MCP server should define tools"
        assert "def " in code or "async def " in code, \
            "MCP server should define handler functions"


class TestLabDocumentation:
    """Tests for lab documentation completeness."""

    @pytest.mark.parametrize("lab_num,lab_name", [
        ("00", "setup"),
        ("01", "understanding-agents"),
        ("02", "azure-mcp-setup"),
        ("03", "spec-driven-development"),
        ("04", "build-rag-pipeline"),
        ("05", "agent-orchestration"),
        ("06", "deploy-with-azd"),
        ("07", "mcp-server"),
    ])
    def test_lab_has_readme(self, lab_num, lab_name):
        """Test that each lab has a README.md."""
        lab_path = LABS_DIR / f"{lab_num}-{lab_name}" / "README.md"

        if not lab_path.exists():
            pytest.skip(f"Lab {lab_num} not found")

        assert lab_path.exists(), f"Lab {lab_num} missing README.md"

        # README should have substantial content
        with open(lab_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert len(content) > 500, f"Lab {lab_num} README seems too short"
        assert "##" in content, f"Lab {lab_num} README should have sections"

    @pytest.mark.parametrize("lab_num,lab_name,has_solution", [
        ("04", "build-rag-pipeline", True),
        ("05", "agent-orchestration", True),
        ("07", "mcp-server", True),
    ])
    def test_lab_has_solution(self, lab_num, lab_name, has_solution):
        """Test that labs with solutions have the solution directory."""
        solution_path = LABS_DIR / f"{lab_num}-{lab_name}" / "solution"

        if not solution_path.parent.exists():
            pytest.skip(f"Lab {lab_num} not found")

        if has_solution:
            assert solution_path.exists(), f"Lab {lab_num} missing solution directory"
            # Should have at least one Python file
            py_files = list(solution_path.glob("*.py"))
            assert len(py_files) > 0, f"Lab {lab_num} solution has no Python files"


class TestKnowledgeBase:
    """Tests for knowledge base article content."""

    def test_kb_has_minimum_articles(self):
        """Test that KB has at least 50 articles as specified."""
        import json

        kb_path = LABS_DIR / "04-build-rag-pipeline" / "data"

        if not kb_path.exists():
            pytest.skip("KB data directory not found")

        # Count articles in JSON files
        total_articles = 0
        for json_file in kb_path.glob("*_kb.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Handle both formats: {"articles": [...]} and [...]
                if isinstance(data, list):
                    total_articles += len(data)
                elif isinstance(data, dict):
                    articles = data.get("articles", [])
                    total_articles += len(articles)

        assert total_articles >= 50, f"Expected 50+ KB articles, found {total_articles}"

    def test_kb_covers_all_departments(self):
        """Test that KB has articles for each department."""
        kb_path = LABS_DIR / "04-build-rag-pipeline" / "data"

        if not kb_path.exists():
            pytest.skip("KB data directory not found")

        # Check for department-specific JSON files
        expected_keywords = ["financial", "registration", "housing", "it", "polic"]
        found_departments = set()

        for json_file in kb_path.glob("*_kb.json"):
            filename = json_file.stem.lower()
            for keyword in expected_keywords:
                if keyword in filename:
                    found_departments.add(keyword)

        # Should have at least 4 departments covered
        assert len(found_departments) >= 4, \
            f"KB should cover at least 4 departments, found: {found_departments}"

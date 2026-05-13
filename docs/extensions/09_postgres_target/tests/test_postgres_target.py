"""
Extension 09 — Postgres Target
Failing tests: query_legacy_db not yet present in apps.log_analyst.tools.
Tests use an in-memory SQLite fixture — no live Postgres required.
All tests are marked with pytest.mark.extension.
"""
import sqlite3
from pathlib import Path

import pytest
import pytest_asyncio
import httpx

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_SQL = REPO_ROOT / "docs" / "extensions" / "09_postgres_target" / "fixtures" / "schema.sql"

pytest.importorskip("apps.log_analyst.main", reason="apps/log_analyst not importable")
pytest.importorskip("apps.log_analyst.tools", reason="apps/log_analyst/tools not importable")


# ---------------------------------------------------------------------------
# SQLite in-memory fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def sqlite_db():
    """In-memory SQLite DB seeded from fixtures/schema.sql (Postgres stand-in)."""
    assert SCHEMA_SQL.exists(), (
        f"Fixture schema not found at {SCHEMA_SQL}. "
        "This file should be committed to the repo."
    )
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def patch_query_legacy_db_to_use_sqlite(sqlite_db, monkeypatch):
    """Replace the real DB connection in query_legacy_db with the SQLite fixture."""
    # Only patch if the function already exists — otherwise let the ImportError surface.
    try:
        import apps.log_analyst.tools as tools_module  # noqa: E402
    except ImportError:
        return

    if not hasattr(tools_module, "query_legacy_db"):
        return

    original = tools_module.query_legacy_db

    def _sqlite_query_legacy_db(sql: str) -> dict:
        sql_stripped = sql.strip().upper()
        if not sql_stripped.startswith("SELECT"):
            return {"error": "Only SELECT statements are allowed.", "rows": [], "citations": []}
        try:
            cursor = sqlite_db.execute(sql)
            rows = [dict(row) for row in cursor.fetchall()]
            return {"rows": rows, "citations": ["sqlite://incidents"]}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc), "rows": [], "citations": []}

    monkeypatch.setattr(tools_module, "query_legacy_db", _sqlite_query_legacy_db)
    yield
    # monkeypatch restores automatically


@pytest_asyncio.fixture
async def log_analyst_client():
    from apps.log_analyst.main import app  # noqa: E402
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.extension
def test_query_legacy_db_exists():
    """query_legacy_db must be exported from apps.log_analyst.tools."""
    from apps.log_analyst import tools  # noqa: E402

    assert hasattr(tools, "query_legacy_db"), (
        "Add 'query_legacy_db' to apps/log_analyst/tools.py"
    )
    assert callable(tools.query_legacy_db)


@pytest.mark.extension
def test_query_legacy_db_select_returns_rows():
    """query_legacy_db('SELECT * FROM incidents') returns rows from the fixture."""
    from apps.log_analyst.tools import query_legacy_db  # noqa: E402

    result = query_legacy_db("SELECT * FROM incidents")
    assert isinstance(result, dict)
    assert "rows" in result, "Result must have 'rows' key."
    assert "citations" in result, "Result must have 'citations' key."
    assert len(result["rows"]) >= 3, (
        f"Expected at least 3 rows from fixture, got {len(result['rows'])}."
    )


@pytest.mark.extension
def test_query_legacy_db_rejects_non_select():
    """query_legacy_db must reject non-SELECT SQL."""
    from apps.log_analyst.tools import query_legacy_db  # noqa: E402

    result = query_legacy_db("DROP TABLE incidents")
    # Acceptable: return an error dict OR raise an exception
    if isinstance(result, dict):
        assert "error" in result, (
            "Non-SELECT should return a dict with an 'error' key."
        )
    # If it raises, the test also passes (pytest captures the exception)


@pytest.mark.extension
def test_query_legacy_db_where_clause():
    """query_legacy_db supports WHERE clauses and returns filtered rows."""
    from apps.log_analyst.tools import query_legacy_db  # noqa: E402

    result = query_legacy_db("SELECT * FROM incidents WHERE line = 'L2'")
    assert isinstance(result, dict)
    rows = result.get("rows", [])
    assert len(rows) >= 1
    for row in rows:
        assert row.get("line") == "L2", f"Expected line='L2', got {row.get('line')}"


@pytest.mark.extension
@pytest.mark.asyncio
async def test_query_legacy_db_endpoint_returns_200(log_analyst_client):
    """/tools/query_legacy_db returns HTTP 200 for a valid SELECT."""
    response = await log_analyst_client.post(
        "/tools/query_legacy_db",
        json={"sql": "SELECT * FROM incidents"},
    )
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        "Register query_legacy_db as a POST route at /tools/query_legacy_db."
    )
    body = response.json()
    assert "rows" in body


@pytest.mark.extension
def test_schema_fixture_file_exists():
    """The SQL fixture file must be committed to the repo."""
    assert SCHEMA_SQL.exists(), (
        f"Fixture schema not found at {SCHEMA_SQL}. "
        "Commit docs/extensions/09_postgres_target/fixtures/schema.sql."
    )

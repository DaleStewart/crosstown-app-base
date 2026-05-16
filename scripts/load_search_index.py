"""Load mock train-control logs and runbooks into Azure AI Search.

Run after `azd up` (azd hook will invoke this).
Requires env vars from `.env.example` to be populated (azd sets them automatically).

Uses Azure SDK with DefaultAzureCredential — no keys.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.cosmos import CosmosClient

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def get_credential() -> TokenCredential:
    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def build_log_index(name: str) -> SearchIndex:
    fields = [
        SimpleField(name="log_id", type=SearchFieldDataType.String, key=True, filterable=True),
        SimpleField(name="timestamp", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True),
        SimpleField(name="line", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="station", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="severity", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="event_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SearchableField(name="message", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SimpleField(name="operator_id", type=SearchFieldDataType.String, filterable=True),
    ]
    semantic = SemanticSearch(configurations=[
        SemanticConfiguration(
            name="default",
            prioritized_fields=SemanticPrioritizedFields(
                content_fields=[SemanticField(field_name="message")],
                keywords_fields=[SemanticField(field_name="event_type")],
            ),
        )
    ])
    return SearchIndex(name=name, fields=fields, semantic_search=semantic)


def build_runbook_index(name: str) -> SearchIndex:
    fields = [
        SimpleField(name="runbook_id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="body", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
    ]
    semantic = SemanticSearch(configurations=[
        SemanticConfiguration(
            name="default",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=SemanticField(field_name="title"),
                content_fields=[SemanticField(field_name="body")],
            ),
        )
    ])
    return SearchIndex(name=name, fields=fields, semantic_search=semantic)


def upsert_index(client: SearchIndexClient, index: SearchIndex) -> None:
    try:
        client.create_or_update_index(index)
        print(f"  upserted index: {index.name}")
    except Exception as exc:  # noqa: BLE001
        print(f"  FAILED to upsert {index.name}: {exc}", file=sys.stderr)
        raise


def load_logs(search_client: SearchClient) -> int:
    path = DATA / "mock_logs" / "logs.jsonl"
    docs: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("{\"_comment\""):
                continue
            docs.append(json.loads(line))
    # batch in chunks of 1000
    total = 0
    for i in range(0, len(docs), 1000):
        chunk = docs[i:i + 1000]
        search_client.upload_documents(documents=chunk)
        total += len(chunk)
    return total


def load_runbooks(search_client: SearchClient) -> int:
    path = DATA / "runbooks"
    docs: list[dict] = []
    for md in sorted(path.glob("*.md")):
        body = md.read_text(encoding="utf-8")
        lines = body.splitlines()
        title = next((ln.lstrip("# ").strip() for ln in lines if ln.startswith("# ")), md.stem)
        docs.append({
            "runbook_id": md.stem,
            "title": title,
            "body": body,
        })
    if docs:
        search_client.upload_documents(documents=docs)
    return len(docs)


def seed_incidents(endpoint: str, db: str, container: str, credential: TokenCredential) -> int:
    path = DATA / "seed_incidents.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    client = CosmosClient(endpoint, credential=credential)
    database = client.get_database_client(db)
    cont = database.get_container_client(container)
    count = 0
    for inc in payload["incidents"]:
        # Cosmos SQL API requires every document to carry a non-empty `id`
        # string. Our seed records only carry `incidentId` (the partition
        # key per architecture contract #6 — see copilot-instructions.md).
        # Mirror it into `id` so upsert succeeds; readers query by
        # `incidentId` so equality is safe (see
        # apps/log_analyst/tools/summarize_incident.py::_fetch_incident).
        if "id" not in inc:
            inc["id"] = str(inc["incidentId"])
        cont.upsert_item(inc)
        count += 1
    return count


def main() -> int:
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    logs_index = os.environ.get("AZURE_SEARCH_INDEX_LOGS", "mta-logs")
    runbooks_index = os.environ.get("AZURE_SEARCH_INDEX_RUNBOOKS", "mta-runbooks")
    cosmos_endpoint = os.environ.get("AZURE_COSMOS_ENDPOINT")
    cosmos_db = os.environ.get("AZURE_COSMOS_DATABASE", "mta")
    cosmos_container = os.environ.get("AZURE_COSMOS_CONTAINER_INCIDENTS", "incidents")

    if not search_endpoint:
        print("AZURE_SEARCH_ENDPOINT not set; skipping search load.", file=sys.stderr)
    if not cosmos_endpoint:
        print("AZURE_COSMOS_ENDPOINT not set; skipping cosmos seed.", file=sys.stderr)

    credential = get_credential()

    if search_endpoint:
        idx_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
        print("Upserting indexes…")
        upsert_index(idx_client, build_log_index(logs_index))
        upsert_index(idx_client, build_runbook_index(runbooks_index))

        print("Loading logs…")
        n_logs = load_logs(SearchClient(endpoint=search_endpoint, index_name=logs_index, credential=credential))
        print(f"  uploaded {n_logs} log docs")

        print("Loading runbooks…")
        n_rb = load_runbooks(SearchClient(endpoint=search_endpoint, index_name=runbooks_index, credential=credential))
        print(f"  uploaded {n_rb} runbook docs")

    if cosmos_endpoint:
        print("Seeding incidents…")
        n_inc = seed_incidents(cosmos_endpoint, cosmos_db, cosmos_container, credential)
        print(f"  upserted {n_inc} incidents")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

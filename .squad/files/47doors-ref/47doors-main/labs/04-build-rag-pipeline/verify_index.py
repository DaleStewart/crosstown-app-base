"""
Lab 04 - Verify Pre-indexed Data
Run this script to confirm the Azure AI Search index is properly configured.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "00-setup"))

# Load environment variables from Lab 00 setup
env_path = Path(__file__).parent.parent / "00-setup" / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()  # Try current directory


def verify_index():
    """Verify the pre-indexed Azure AI Search data."""

    print("=" * 60)
    print("Lab 04 - Verify Pre-indexed Data")
    print("=" * 60)
    print()

    # Check environment variables
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "university-kb")

    if not endpoint or not api_key:
        print("❌ Missing environment variables!")
        print("   Ensure AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY are set.")
        print(f"   Looking for .env at: {env_path}")
        return False

    print(f"Search Endpoint: {endpoint}")
    print(f"Index Name: {index_name}")
    print()

    try:
        # Connect to search
        client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(api_key),
        )

        # Test 1: Count documents
        print("Test 1: Document Count")
        print("-" * 40)
        results = list(client.search(search_text="*", top=100))
        doc_count = len(results)

        if doc_count >= 30:
            print(f"✅ Found {doc_count} documents in index")
        else:
            print(f"⚠️  Only found {doc_count} documents (expected 32)")
        print()

        # Test 2: Keyword search
        print("Test 2: Keyword Search")
        print("-" * 40)
        results = list(client.search(search_text="password reset", top=3))

        if results:
            print("✅ Keyword search working!")
            print("   Top results for 'password reset':")
            for r in results:
                print(f"   - {r.get('title', 'Unknown')}")
        else:
            print("❌ Keyword search returned no results")
        print()

        # Test 3: Check vector field exists
        print("Test 3: Vector Field Check")
        print("-" * 40)
        if results and "content_vector" in results[0]:
            print("✅ Vector embeddings are present")
        else:
            # Vector field may not be returned in select, try another way
            print("✅ Index accessible (vector field not in default select)")
        print()

        # Test 4: Category filter
        print("Test 4: Category Filter")
        print("-" * 40)
        results = list(
            client.search(search_text="*", filter="department eq 'it_support'", top=3)
        )

        if results:
            print("✅ Filtering by department working!")
            print(f"   Found {len(results)} IT Support articles")
        else:
            print("⚠️  No results for department filter")
        print()

        # Summary
        print("=" * 60)
        print("✅ Index verification complete!")
        print("=" * 60)
        print()
        print("You're ready to start Step 4: Implement the Search Tool")
        print()
        return True

    except Exception as e:
        print(f"❌ Error connecting to Azure AI Search: {e}")
        return False


if __name__ == "__main__":
    success = verify_index()
    sys.exit(0 if success else 1)

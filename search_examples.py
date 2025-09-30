#!/usr/bin/env python3
"""
Example usage scripts for Chabad text search
"""

from chabad_text_search import ChabadTextSearch
from pathlib import Path

def search_lechatchila_arieber():
    """Search for לכתחילה אריבער examples"""
    searcher = ChabadTextSearch("/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads")

    print("=== Searching for לכתחילה אַריבער ===")
    results = searcher.search_all("אַריבער", case_sensitive=False)

    print(f"Found {len(results)} results")
    for result in results:
        print(f"\nBook: {result.book_name}")
        print(f"Section: {result.chunk_title}")
        print(f"Context: ...{result.context_before[-150:]} **{result.match_text}** {result.context_after[:150]}...")
        print("-" * 80)

def search_teshuvah_concepts():
    """Search for teshuvah-related concepts"""
    searcher = ChabadTextSearch("/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads")

    concepts = [
        "תמים תהיה",
        "שויתי ה' לנגדי",
        "ואהבת לרעך כמוך",
        "בכל דרכיך דעהו",
        "הצנע לכת"
    ]

    for concept in concepts:
        print(f"\n=== Searching for {concept} ===")
        results = searcher.search_all(concept)
        print(f"Found {len(results)} results")

        if results:
            # Show first result as example
            result = results[0]
            print(f"Example from: {result.book_name}")
            print(f"Context: {result.context_before[-100:]} **{result.match_text}** {result.context_after[:100]}")

def search_in_specific_collection(collection_name: str, pattern: str):
    """Search within a specific collection"""
    searcher = ChabadTextSearch("/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads")

    results = searcher.search_all(pattern, file_filter=collection_name, verbose=True)

    print(f"=== Results for '{pattern}' in {collection_name} ===")
    formatted_results = searcher.format_results(results, max_results=10, show_context=True)
    print(formatted_results)

    return results

if __name__ == "__main__":
    # Example usage
    print("Chabad Text Search Examples")
    print("=" * 50)

    # Search for לכתחילה אריבער
    search_lechatchila_arieber()

    # Search in Toras Menachem specifically
    print("\n" + "=" * 50)
    results = search_in_specific_collection("Toras Menachem", "לכתחילה אַריבער")

    # Export results
    if results:
        searcher = ChabadTextSearch("/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads")
        searcher.export_results(results, "lechatchila_arieber_results.json", "json")
        searcher.export_results(results, "lechatchila_arieber_results.txt", "txt")
#!/usr/bin/env python3
"""Simple test script for the search API"""

import requests
import json

def test_search(search_term, use_ai=False):
    """Test the search API with a given term"""
    url = "http://localhost:8080/api/search"

    payload = {
        "search_term": search_term,
        "anthropic_api_key": "demo_key"  # Demo mode for testing
    }

    print(f"\n🔍 Testing search for: {search_term}")
    print("=" * 60)

    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()

        if data.get('success'):
            print(f"✅ Success!")
            print(f"📊 Found {data.get('result_count', 0)} results")

            if data.get('analysis'):
                # Strip HTML for display
                analysis = data['analysis']
                if len(analysis) > 500:
                    print(f"\n📝 Analysis preview (first 500 chars):")
                    print(analysis[:500] + "...")
                else:
                    print(f"\n📝 Analysis:")
                    print(analysis)
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    # Test with Hebrew terms
    test_search("משתשקע החמה")
    test_search("בת ציון")
    test_search("שבת")

    # Test with English
    test_search("malchus")

    print("\n" + "=" * 60)
    print("✅ Tests complete!")
#!/usr/bin/env python3
"""
Demo CORS proxy server for GitHub Pages deployment
Uses sample responses instead of local dataset
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Sample Chabad content for demo
SAMPLE_RESPONSES = {
    "בנין המלכות": """דע, דברכת כהנים - "יברכך ה' וישמרך" - מדובר על בנין המלכות העליונה.
    כמו שכתב האריז"ל בפרי עץ חיים, שמלכות היא הספירה התחתונה שמקבלת מכל הספירות העליונות.

    ובלקוטי תורה מבואר, שכל ישראל הם "ממלכת כהנים וגוי קדוש", ועל ידי עבודתם הם בונים את המלכות דקדושה.""",

    "ברכת כהנים": """ברכת כהנים מורכבת משלושה פסוקים:
    יברכך ה' וישמרך - ברכה גשמית
    יאר ה' פניו אליך - ברכה רוחנית
    ישא ה' פניו אליך - שלום

    ובתורת חב"ד מבואר שהברכות הללו מתייחסות לשלוש הקווים - ימין, שמאל, ואמצע.""",

    "ששים גבורים": """ששים גבורים סביב למטתו של שלמה - אלו ששים אלף אותיות התורה.
    כל אות בתורה היא כמו גבור השומר על קדושת התורה.

    וכמו שמבואר בזוהר, ששים הוא מספר המייצג שלמות וגבורה."""
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'dataset_accessible': True, 'mode': 'demo'})

@app.route('/search', methods=['POST', 'OPTIONS'])
def demo_search():
    """Demo search with sample responses"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json(force=True)
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Empty query provided'}), 400

        # Check if we have a sample response
        sample_response = None
        for key, response in SAMPLE_RESPONSES.items():
            if key in query or query in key:
                sample_response = response
                break

        if not sample_response:
            sample_response = f"""דוגמה לתוצאה עבור "{query}":

זוהי גרסת דמו של חיפוש בקורפוס החסידי. בגרסה המלאה, החיפוש יתבצע במאגר המלא של כל הספרים החסידיים.

התוצאות יכללו:
• קטעים מתורת חב"ד
• מקורות מהזוהר ומהאריז"ל
• הסברים בעברית, יידיש ואנגלית
• ציוני מקורות מדויקים

זוהי תצוגה מקדימה בלבד."""

        # Create demo response
        return jsonify({
            'query': query,
            'search_results_count': 3,
            'analysis': {
                'content': [{
                    'text': sample_response
                }]
            },
            'raw_search_results': [
                {
                    'source': 'demo_sample',
                    'content': f'דוגמה לתוצאה מחיפוש עבור "{query}" במאגר החסידי'
                }
            ],
            'demo_mode': True
        })

    except Exception as e:
        return jsonify({'error': f'Demo error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    print(f"🚀 Starting Demo Chabad Search Proxy on port {port}...")
    print("   This is DEMO MODE with sample responses")
    app.run(host='0.0.0.0', port=port, debug=False)
#!/usr/bin/env python3
"""
Enhanced CORS proxy server that searches Chabad dataset and uses Claude for analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import subprocess
import glob

app = Flask(__name__)
CORS(app)  # Allow all origins

# Chabad dataset path
CHABAD_DATA_PATH = "/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads"
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', 'your-api-key-here')  # Set via environment variable

def search_chabad_files(query):
    """Search through Chabad files for the query term"""
    search_results = []

    try:
        # Use ripgrep to search for the query in all JSON files
        cmd = [
            '/Users/elishapearl/.nvm/versions/node/v22.14.0/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg',
            '-n', '-C', '2',  # line numbers and 2 lines context
            '--type', 'json',
            query,
            CHABAD_DATA_PATH
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0 and result.stdout:
            search_results.append({
                'source': 'ripgrep_json',
                'content': result.stdout[:5000]  # Limit content size
            })

        # Also search in text files
        cmd_txt = [
            '/Users/elishapearl/.nvm/versions/node/v22.14.0/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg',
            '-n', '-C', '2',
            '--type', 'txt',
            query,
            CHABAD_DATA_PATH
        ]

        result_txt = subprocess.run(cmd_txt, capture_output=True, text=True, timeout=30)

        if result_txt.returncode == 0 and result_txt.stdout:
            search_results.append({
                'source': 'ripgrep_txt',
                'content': result_txt.stdout[:5000]  # Limit content size
            })

    except subprocess.TimeoutExpired:
        search_results.append({
            'source': 'error',
            'content': 'Search timeout - dataset is very large'
        })
    except Exception as e:
        search_results.append({
            'source': 'error',
            'content': f'Search error: {str(e)}'
        })

    return search_results

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'dataset_accessible': os.path.exists(CHABAD_DATA_PATH)})

@app.route('/search', methods=['POST', 'OPTIONS'])
def search_and_analyze():
    """Search Chabad dataset and analyze with Claude"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
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
        context = data.get('context', '').strip()

        if not query:
            return jsonify({'error': 'Empty query provided'}), 400

        # Step 1: Search the Chabad dataset
        print(f"Searching for: {query}")
        search_results = search_chabad_files(query)

        if not search_results or all(r.get('source') == 'error' for r in search_results):
            return jsonify({
                'error': 'No results found in Chabad dataset',
                'search_results': search_results
            }), 404

        # Step 2: Build prompt with search results
        prompt = f"""I found the following results searching for "{query}" in the Chabad Chassidic literature dataset:

SEARCH RESULTS FROM CHABAD DATASET:
"""

        for i, result in enumerate(search_results, 1):
            if result.get('source') != 'error':
                prompt += f"\n=== RESULT {i} ===\n"
                prompt += result['content']
                prompt += "\n"

        if context:
            prompt += f"\nADDITIONAL CONTEXT: {context}\n"

        prompt += f"""

Based on these actual search results from the Chabad literature dataset, please provide:

1. **Hebrew Sources** - Extract and present the most relevant Hebrew passages
2. **Source Attribution** - Identify the exact texts and discourse titles (ד"ה) where found
3. **Three Main Explanations** - Analyze the three primary ways "{query}" is explained
4. **Multi-language Analysis** - Provide explanations in:
   - Hebrew (עברית)
   - Yiddish (יידיש)
   - English

Focus on the actual content found in the search results above. Include proper source citations from the search results.
"""

        # Step 3: Send to Claude for analysis
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 4000,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=60
        )

        if response.status_code == 200:
            claude_result = response.json()
            return jsonify({
                'query': query,
                'search_results_count': len([r for r in search_results if r.get('source') != 'error']),
                'analysis': claude_result,
                'raw_search_results': search_results  # For debugging
            })
        else:
            error_msg = f'Claude API error: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text}'
            return jsonify({'error': error_msg}), response.status_code

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Chabad Search Proxy...")
    print(f"   Server: http://localhost:3001")
    print(f"   Health: http://localhost:3001/health")
    print(f"   Search: POST to http://localhost:3001/search")
    print(f"   Dataset: {CHABAD_DATA_PATH}")
    print(f"   Dataset exists: {os.path.exists(CHABAD_DATA_PATH)}")
    print("\n   Now open enhanced_demo.html in your browser!")

    app.run(host='0.0.0.0', port=3001, debug=False)
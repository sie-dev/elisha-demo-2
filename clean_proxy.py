#!/usr/bin/env python3
"""
Clean CORS proxy server for Claude API calls with embedded API key
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # Allow all origins

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/claude', methods=['POST', 'OPTIONS'])
def proxy_claude():
    """Proxy requests to Claude API with embedded key"""
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json(force=True)
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing prompt in request data'}), 400

        prompt = data['prompt']
        if not prompt:
            return jsonify({'error': 'Empty prompt provided'}), 400

        # Get API key from environment
        api_key = os.getenv('CLAUDE_API_KEY', 'your-api-key-here')

        # Make request to Claude API
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 4000,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return jsonify(result)
        else:
            error_msg = f'Claude API error: {response.status_code}'
            if response.text:
                error_msg += f' - {response.text}'
            return jsonify({'error': error_msg}), response.status_code

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Clean CORS Proxy Server...")
    print("   Server: http://localhost:3001")
    print("   Health: http://localhost:3001/health")
    print("   Claude: POST to http://localhost:3001/claude")
    print("   API Key: Embedded (no user input required)")
    print("\n   Ready for public demo!")

    app.run(host='0.0.0.0', port=3001, debug=False)
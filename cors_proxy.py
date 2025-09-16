#!/usr/bin/env python3
"""
Simple CORS proxy server for Claude API calls
Allows the demo to work from local HTML files
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # Allow all origins

@app.route('/claude', methods=['POST'])
def proxy_claude():
    """Proxy requests to Claude API with CORS headers"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'error': 'Missing prompt'}), 400

        # Get API key from environment variable
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
                'model': 'claude-3-sonnet-20240229',
                'max_tokens': 4000,
                'messages': [{'role': 'user', 'content': prompt}]
            }
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': f'Claude API error: {response.status_code}'}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 Starting CORS proxy server for Claude API...")
    print("   Server: http://localhost:3001")
    print("   Health: http://localhost:3001/health")
    print("   Claude: POST to http://localhost:3001/claude")
    print("\n   Now open dropbox_demo.html in your browser!")
    app.run(host='0.0.0.0', port=3001, debug=True)
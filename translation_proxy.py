#!/usr/bin/env python3
"""
Enhanced proxy server with translation feature for Chabad sefarim
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import subprocess
import glob

app = Flask(__name__)
CORS(app)

# Paths
CHABAD_DATA_PATH = "/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads"
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', 'your-api-key-here')

def list_sefarim():
    """List all available sefarim in the Dropbox folder"""
    try:
        sefarim = []
        if os.path.exists(CHABAD_DATA_PATH):
            # Find all text and JSON files
            for pattern in ['*.txt', '*.json']:
                files = glob.glob(os.path.join(CHABAD_DATA_PATH, '**', pattern), recursive=True)
                for filepath in files:
                    rel_path = os.path.relpath(filepath, CHABAD_DATA_PATH)
                    filename = os.path.basename(filepath)
                    sefarim.append({
                        'name': filename,
                        'path': rel_path,
                        'size': os.path.getsize(filepath)
                    })
        return sefarim
    except Exception as e:
        return []

def get_file_chunks(filepath, chunk_size=2000):
    """Break a sefer into translatable chunks"""
    try:
        full_path = os.path.join(CHABAD_DATA_PATH, filepath)
        if not os.path.exists(full_path):
            return []

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into chunks of ~2000 characters
        chunks = []
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            chunks.append({
                'index': len(chunks),
                'content': chunk,
                'start_pos': i,
                'end_pos': min(i+chunk_size, len(content))
            })

        return chunks
    except Exception as e:
        return []

def translate_chunk(chunk_text, target_language='English'):
    """Translate a chunk using Claude"""
    try:
        prompt = f"""אתה מתרגם מומחה של ספרות חסידית חב"ד. תרגם את הקטע הבא ל{target_language}:

{chunk_text}

**הנחיות לתרגום:**

1. **טון אקדמי-רוחני:** שמור על הטון המלומד והרוחני של המקור החסידי
2. **מונחים טכניים:** עבור מונחי קבלה וחסידות - ספק הן את התעתיק והן הסבר קצר
   - דוגמאות: ספירות, צמצום, ביטול, התבוננות, עבודת הברירות
3. **אותנטיות:** שמור על המשמעות המקורית ועל כבוד הטקסט
4. **בהירות:** תרגם בצורה ברורה וקריאה לקוראים שאינם בקיאים בטקסטים חסידיים
5. **הקשר מערכתי:** הסבר קשרים לרעיונות מרכזיים בחב"ד כמו אחדות הוי' ויחודו

**פורמט התרגום:**
- תרגום ראשי ברור
- הערות הסבר בסוגריים [אם נדרש]
- גלוסריום למונחים מיוחדים

התמקד בהעברת הלימוד החסידי העמוק תוך שמירה על כבוד הטקסט המקודש."""

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': CLAUDE_API_KEY,
                'anthropic-version': '2023-06-01'
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 3000,
                'messages': [{'role': 'user', 'content': prompt}]
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result['content'][0]['text']
        else:
            return f"Translation error: {response.status_code}"

    except Exception as e:
        return f"Translation failed: {str(e)}"

@app.route('/sefarim', methods=['GET'])
def get_sefarim_list():
    """Get list of all available sefarim"""
    sefarim = list_sefarim()
    return jsonify({
        'sefarim': sefarim,
        'count': len(sefarim)
    })

@app.route('/sefer/<path:filepath>/chunks', methods=['GET'])
def get_sefer_chunks(filepath):
    """Get chunks of a specific sefer for translation"""
    chunks = get_file_chunks(filepath)
    return jsonify({
        'filepath': filepath,
        'chunks': chunks[:10],  # Return first 10 chunks
        'total_chunks': len(chunks)
    })

@app.route('/translate', methods=['POST'])
def translate_chunk_endpoint():
    """Translate a specific chunk"""
    try:
        data = request.get_json()
        chunk_text = data.get('text', '')
        target_lang = data.get('target_language', 'English')

        if not chunk_text.strip():
            return jsonify({'error': 'No text provided'}), 400

        translation = translate_chunk(chunk_text, target_lang)

        return jsonify({
            'original': chunk_text,
            'translation': translation,
            'target_language': target_lang
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'dataset_accessible': os.path.exists(CHABAD_DATA_PATH),
        'features': ['search', 'translate', 'sefarim_list']
    })

# Keep existing search functionality
def search_chabad_files(query):
    """Search through Chabad files for the query term"""
    search_results = []
    try:
        cmd = [
            '/Users/elishapearl/.nvm/versions/node/v22.14.0/lib/node_modules/@anthropic-ai/claude-code/vendor/ripgrep/arm64-darwin/rg',
            '-n', '-C', '2',
            '--type', 'json',
            query,
            CHABAD_DATA_PATH
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout:
            search_results.append({
                'source': 'ripgrep_json',
                'content': result.stdout[:3000]
            })
    except Exception as e:
        search_results.append({
            'source': 'error',
            'content': f'Search error: {str(e)}'
        })
    return search_results

@app.route('/search', methods=['POST', 'OPTIONS'])
def search_and_analyze():
    """Existing search functionality"""
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    try:
        data = request.get_json(force=True)
        query = data['query'].strip()

        # Search the dataset
        search_results = search_chabad_files(query)

        if not search_results or all(r.get('source') == 'error' for r in search_results):
            return jsonify({
                'error': 'No results found in Chabad dataset',
                'search_results': search_results
            }), 404

        # Build prompt for Claude analysis
        prompt = f"""אתה מומחה בתורת חב"ד ובפילוסופיה חסידית. נמצאו תוצאות לחיפוש "{query}" במאגר החסידי:

{search_results[0]['content']}

אנא ספק ניתוח מקיף כדלקמן:

**בעברית:** הסבר מעמיק על המושג "{query}" על פי מקורות חב"ד, כולל:
- הקשר למערכת הספירות
- השלכות עבודת ה' האישית
- קישורים לנושאים נוספים במערכת החסידית

**באנגלית:** Detailed scholarly analysis including:
- Theological significance in Chabad philosophy
- Connection to core Kabbalistic concepts
- Practical implications for divine service

**ציטוטים:** ציין בבירור מהם הד"ה (דיבור המתחיל) ומקורות אחרים הנזכרים בקטע.

התמקד במשמעות הרוחנית העמוקה ובחיבור למערכת החסידית הכוללת."""

        # Send to Claude
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
            timeout=120
        )

        if response.status_code == 200:
            claude_result = response.json()
            return jsonify({
                'query': query,
                'search_results_count': len([r for r in search_results if r.get('source') != 'error']),
                'analysis': claude_result,
                'raw_search_results': search_results
            })
        else:
            return jsonify({'error': f'Claude API error: {response.status_code}'}), response.status_code

    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Translation-Enabled Chabad Proxy...")
    print(f"   Server: http://localhost:3001")
    print(f"   Dataset: {CHABAD_DATA_PATH}")
    print(f"   Features: Search + Translation")

    app.run(host='0.0.0.0', port=3001, debug=False)
#!/usr/bin/env python3
"""
Chabad Torah Search Interface - Backend Server
Provides API endpoints for searching and analyzing Chabad literature
"""

import os
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import anthropic
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@dataclass
class SearchResult:
    file_path: str
    chunk_id: str
    chunk_title: str
    discourse_title: str
    text: str
    author: str
    work: str
    metadata: Dict[str, Any]

class ChabadSearchService:
    def __init__(self, sichos_file: str, maamarim_file: str):
        """Initialize with specific sichos and maamarim files"""
        self.sichos_file = Path(sichos_file)
        self.maamarim_file = Path(maamarim_file)

        # Common question words to strip from searches
        self.question_words = [
            'מה', 'מהו', 'מהי', 'איך', 'למה', 'מדוע', 'כיצד', 'מתי',
            'what', 'how', 'why', 'when', 'where', 'explain', 'tell', 'is', 'are', 'and', 'the', 'a', 'an',
            'זה', 'זו', 'את', 'הסבר', 'תסביר', 'ביאור', 'של', 'ו', 'ה'
        ]

        # Common transliterations and translations
        self.term_translations = {
            # Malchus
            'malchus': 'מלכות',
            'malchut': 'מלכות',
            'malchuts': 'מלכות',

            # Mihu Yehudi
            'mihu': 'מיהו',
            'yehudi': 'יהודי',
            'jew': 'יהודי',
            'jewish': 'יהודי',

            # Common terms
            'shabbat': 'שבת',
            'shabbos': 'שבת',
            'chanukah': 'חנוכה',
            'hanukkah': 'חנוכה',
            'chanuka': 'חנוכה',
            'rebbe': 'רבי',
            'rabbi': 'רב',
            'chassidus': 'חסידות',
            'chassidut': 'חסידות',
            'hasidus': 'חסידות',
            'torah': 'תורה',
            'teshuvah': 'תשובה',
            'teshuva': 'תשובה',
        }

        if not self.sichos_file.exists():
            raise ValueError(f"Sichos file not found: {sichos_file}")
        if not self.maamarim_file.exists():
            raise ValueError(f"Maamarim file not found: {maamarim_file}")

        # Load both files into memory for faster searching
        logger.info("Loading sichos data...")
        with open(self.sichos_file, 'r', encoding='utf-8') as f:
            self.sichos_data = json.load(f)

        logger.info("Loading maamarim data...")
        with open(self.maamarim_file, 'r', encoding='utf-8') as f:
            self.maamarim_data = json.load(f)

        logger.info(f"Loaded {len(self.sichos_data.get('chunks', []))} sichos chunks")
        logger.info(f"Loaded {len(self.maamarim_data.get('chunks', []))} maamarim chunks")

    def search_in_chunks(self, search_term: str) -> List[SearchResult]:
        """Search for term in all chunks from both files"""
        results = []

        # Search in sichos
        sichos_results = self._search_in_data(
            self.sichos_data,
            search_term,
            'sichos',
            str(self.sichos_file)
        )
        results.extend(sichos_results)

        # Search in maamarim
        maamarim_results = self._search_in_data(
            self.maamarim_data,
            search_term,
            'maamarim',
            str(self.maamarim_file)
        )
        results.extend(maamarim_results)

        logger.info(f"Found {len(results)} matching chunks for '{search_term}'")
        return results

    def _search_in_data(self, data: Dict, search_term: str, source_type: str, file_path: str) -> List[SearchResult]:
        """Search for term in chunks from a single file"""
        results = []
        book_name = data.get('book_name_he', '') or data.get('book_name_en', '')
        author = data.get('book_metadata', {}).get('author_he', '') or data.get('book_metadata', {}).get('author_en', '')

        chunks = data.get('chunks', [])
        search_lower = search_term.lower()

        for chunk in chunks:
            text = chunk.get('text', '')
            # Case-insensitive search that works with Hebrew/English/Yiddish
            if search_lower in text.lower() or search_term in text:
                result = SearchResult(
                    file_path=file_path,
                    chunk_id=chunk.get('chunk_id', ''),
                    chunk_title=chunk.get('chunk_metadata', {}).get('chunk_title', ''),
                    discourse_title=self._extract_discourse_title(chunk),
                    text=text,
                    author=author,
                    work=book_name,
                    metadata=chunk.get('chunk_metadata', {})
                )
                results.append(result)

        return results

    def _extract_discourse_title(self, chunk: Dict) -> str:
        """Extract the discourse title (ד״ה) from chunk metadata"""
        metadata = chunk.get('chunk_metadata', {})

        # Try various fields that might contain the discourse title
        for field in ['dibbur_hamaschil', 'maamar', 'discourse_title']:
            if field in metadata:
                return metadata[field]

        # Try to extract from chunk title
        chunk_title = metadata.get('chunk_title', '')
        if 'ד״ה' in chunk_title:
            # Extract the part after ד״ה
            match = re.search(r'ד״ה\s*([^/]+)', chunk_title)
            if match:
                return f"ד״ה {match.group(1).strip()}"

        return ''

    def extract_search_terms(self, query: str) -> List[str]:
        """Extract key search terms from a natural language query"""
        # Remove punctuation
        query = query.replace('?', '').replace('!', '').replace('.', '').replace(',', '')

        # Split into words
        words = query.split()

        # Translate English/transliterated words to Hebrew
        translated_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower in self.term_translations:
                translated_words.append(self.term_translations[word_lower])
            else:
                translated_words.append(word)

        # Remove common question words
        key_words = [w for w in translated_words if w.lower() not in self.question_words]

        # Return both the cleaned query and individual key terms
        cleaned_query = ' '.join(key_words)

        search_terms = []
        if cleaned_query:
            search_terms.append(cleaned_query)

        # Also add longer phrases (2-4 words) for better matching
        if len(key_words) >= 2:
            for i in range(len(key_words)):
                for j in range(i + 2, min(i + 5, len(key_words) + 1)):
                    phrase = ' '.join(key_words[i:j])
                    if phrase and phrase not in search_terms:
                        search_terms.append(phrase)

        # Add individual significant words (3+ chars)
        for word in key_words:
            if len(word) >= 3 and word not in search_terms:
                search_terms.append(word)

        return search_terms if search_terms else [query]

    def search_concept(self, search_term: str, context: str = '', max_results: int = 15) -> List[SearchResult]:
        """Main search function that finds and processes results"""
        logger.info(f"Original query: {search_term}")

        # Extract search terms
        search_terms = self.extract_search_terms(search_term)
        logger.info(f"Extracted search terms: {search_terms}")

        # Search with each term and combine results
        all_results = []
        seen_chunks = set()

        for term in search_terms:
            results = self.search_in_chunks(term)
            for result in results:
                chunk_key = (result.file_path, result.chunk_id)
                if chunk_key not in seen_chunks:
                    all_results.append(result)
                    seen_chunks.add(chunk_key)

            # If we found enough results with the first term, stop
            if len(all_results) >= max_results:
                break

        logger.info(f"Found {len(all_results)} total matching chunks")

        # Sort by relevance - prioritize matches with more search terms
        def relevance_score(result: SearchResult) -> Tuple[int, int, int]:
            # Count how many search terms appear in the text
            term_count = sum(1 for term in search_terms if term in result.text)

            # Check for exact query match
            exact_match = 1 if search_term in result.text else 0

            # Prefer texts between 500-2000 chars (focused but complete)
            text_len = len(result.text)
            if 500 <= text_len <= 2000:
                length_score = 1000
            else:
                length_score = -abs(text_len - 1000)

            return (-term_count, -exact_match, length_score)

        all_results.sort(key=relevance_score)

        return all_results[:max_results]

class ChabadAnalyzer:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    def analyze_search_results(self, search_term: str, results: List[SearchResult],
                             context: str = '', conversation_history: List[Dict] = None) -> str:
        """Use Claude to analyze search results with conversation context"""

        # Use only top 3 for speed
        top_results = results[:3]

        # Prepare EXCERPTS for Claude analysis (not full text to save time)
        results_text = self._format_excerpts_for_analysis(top_results)

        # Detect if query is in Hebrew, Yiddish, or English
        language_instruction = ""
        if context and 'english' in context.lower():
            language_instruction = "Please respond primarily in English."
        elif any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in search_term):
            language_instruction = "נא להשיב בעברית בעיקר, עם הסברים גם באידיש ובאנגלית כשמתאים."
        else:
            language_instruction = "Please respond with explanations in Hebrew, Yiddish (where relevant), and English."

        # Build system prompt
        system_prompt = """אתה חברותא AI מומחה בחסידות חב"ד, במיוחד בשיחות ומאמרים של הרבי מתשל"ה.

אתה יכול:
- לענות על שאלות ישירות על מושגים חסידיים
- להמשיך שיחות ולענות על שאלות המשך
- להסביר בעברית, אידיש, ואנגלית
- לתת דוגמאות נוספות ולהעמיק כשמבקשים
- לקשר בין מושגים שונים

כשעונה:
- תן הסבר מעמיק ומפורט (4-6 פסקאות)
- הסבר את הרעיון הפנימי, לא רק הפשט
- קשר למושגים אחרים בחסידות
- תן דוגמאות מהמקורות
- הסבר למעשה בעבודת ה'
- השתמש ב-HTML עם dir="rtl" וכותרות <h3>
- אל תכלול את הטקסט המלא של המקורות - הם מתווספים אחרי"""

        # Build messages for conversation
        messages = []

        # Add conversation history if exists
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        # Check if this is a follow-up question (no search results needed)
        is_followup = conversation_history and len(conversation_history) > 0 and len(results) == 0

        if is_followup:
            # Natural conversation without new sources
            user_message = f"שאלת המשך: {search_term}"
        else:
            # New search with sources
            user_message = f"""שאלה: "{search_term}"

נמצאו {len(top_results)} מקורות רלוונטיים:

{results_text}

תן הסבר מעמיק ומפורט (4-6 פסקאות) הכולל:
- מהו המושג ומה משמעותו
- העיקרים והרעיונות המרכזיים מהמקורות
- קשרים למושגים אחרים בחסידות
- דוגמאות והמחשות
- למעשה בעבודת ה'"""

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=3072,  # Increased for deeper analysis
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _format_results_for_analysis(self, results: List[SearchResult]) -> str:
        """Format search results for Claude analysis - FULL CHUNKS"""
        formatted = []

        # Limit to top 3 most relevant results for faster processing
        top_results = results[:3]

        for i, result in enumerate(top_results, 1):
            # Include metadata for context
            metadata = result.metadata
            source_type = metadata.get('type', '')  # שיחה or מאמר
            seif = metadata.get('seif', metadata.get('perek', ''))

            # Get additional context
            farbrengen = metadata.get('farbrengen', '')
            sicha = metadata.get('sicha', '')
            maamar_type = metadata.get('maamar_type', '')

            formatted.append(f"""
{'='*80}
מקור {i} מתוך {len(top_results)}
{'='*80}

סוג: {source_type}
מחבר: {result.author}
ספר: {result.work}
כותרת מלאה: {result.chunk_title}
{f'פרבענגען: {farbrengen}' if farbrengen else ''}
{f'שיחה: {sicha}' if sicha else ''}
{f'סוג מאמר: {maamar_type}' if maamar_type else ''}
סעיף/פרק: {seif}

--- טקסט מלא של הקטע ---

{result.text}

{'='*80}

""")

        summary = f"\nסה״כ נמצאו {len(results)} מקורות. מוצגים {len(top_results)} המקורות הרלוונטיים ביותר עם הטקסט המלא של כל קטע.\n\n"

        return summary + '\n'.join(formatted)

    def _format_excerpts_for_analysis(self, results: List[SearchResult]) -> str:
        """Format EXCERPTS for fast Claude analysis"""
        formatted = []

        for i, result in enumerate(results, 1):
            metadata = result.metadata
            source_type = metadata.get('type', '')
            seif = metadata.get('seif', metadata.get('perek', ''))

            # Use first 800 chars for analysis
            excerpt = result.text[:800]

            formatted.append(f"""
מקור {i}:
סוג: {source_type} | סעיף: {seif}
כותרת: {result.chunk_title}

קטע: {excerpt}...

---
""")

        return '\n'.join(formatted)

# Flask API endpoints
search_service = None
analyzer = None

@app.route('/')
def serve_index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """Main search endpoint"""
    try:
        data = request.get_json()
        search_term = data.get('search_term', '').strip()
        context = data.get('context', '').strip()
        max_results = int(data.get('max_results', 15))
        conversation_history = data.get('conversation_history', [])

        # Get API key from environment variable or request
        anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY', data.get('anthropic_api_key', '')).strip()

        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        # Initialize services
        global search_service, analyzer

        # Check for environment variables first (Railway), then fallback to repo data, then local
        sichos_file = os.environ.get('SICHOS_FILE',
            'data/sichos.json' if Path('data/sichos.json').exists()
            else "/Users/elishapearl/Downloads/sichos_structured (4).json")
        maamarim_file = os.environ.get('MAAMARIM_FILE',
            'data/maamarim.json' if Path('data/maamarim.json').exists()
            else "/Users/elishapearl/Downloads/maamarim_structured (2).json")

        if search_service is None:
            logger.info("Initializing search service...")
            logger.info(f"Sichos file: {sichos_file}")
            logger.info(f"Maamarim file: {maamarim_file}")
            search_service = ChabadSearchService(sichos_file, maamarim_file)

        # Perform search
        results = search_service.search_concept(search_term, context, max_results)

        if not results:
            no_results_msg = f'<div dir="rtl" style="padding: 20px;"><h3>לא נמצאו תוצאות</h3><p>לא נמצאו תוצאות עבור "<strong>{search_term}</strong>" בסיכות ומאמרים של תשל״ה.</p><p>נסה חיפוש אחר או בדוק את האיות.</p></div>'
            return jsonify({
                'success': True,
                'analysis': no_results_msg,
                'result_count': 0
            })

        # Check if we have a valid API key for AI analysis
        if not anthropic_api_key or anthropic_api_key == 'demo_key':
            # Demo mode - show raw results without AI analysis
            demo_analysis = f'<div dir="rtl" style="padding: 20px;"><h3>נמצאו {len(results)} תוצאות עבור "{search_term}"</h3>'
            demo_analysis += '<p style="color: #666; margin: 15px 0;"><em>מציג תוצאות ללא ניתוח AI (נדרש מפתח API)</em></p>'

            for i, result in enumerate(results[:5], 1):
                metadata = result.metadata
                source_type = metadata.get('type', '')
                seif = metadata.get('seif', metadata.get('perek', ''))

                demo_analysis += f'''
                <div style="margin: 20px 0; padding: 20px; border-right: 4px solid #C79A51; background: #f9f9f9; border-radius: 8px;">
                    <h4 style="color: #C79A51; margin-bottom: 10px;">{source_type} - סעיף {seif}</h4>
                    <p style="margin: 5px 0;"><strong>מקור:</strong> {result.author} - {result.work}</p>
                    <p style="margin: 5px 0;"><strong>כותרת:</strong> {result.chunk_title}</p>
                    <hr style="margin: 15px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="margin-top: 15px; line-height: 1.8; font-family: 'Times New Roman', serif;">{result.text[:800]}{'...' if len(result.text) > 800 else ''}</p>
                </div>
                '''

            if len(results) > 5:
                demo_analysis += f'<p style="color: #888; text-align: center; margin-top: 20px;"><em>ועוד {len(results) - 5} תוצאות נוספות...</em></p>'

            demo_analysis += '</div>'

            return jsonify({
                'success': True,
                'analysis': demo_analysis,
                'result_count': len(results)
            })

        # AI analysis with valid API key
        if analyzer is None or analyzer.client.api_key != anthropic_api_key:
            analyzer = ChabadAnalyzer(anthropic_api_key)

        analysis = analyzer.analyze_search_results(search_term, results, context, conversation_history)

        # Append ALL full sources after AI analysis
        sources_html = f'<div dir="rtl"><h3 style="color: #C79A51; margin-top: 2rem; border-top: 2px solid #e5e7eb; padding-top: 1rem;">📖 כל המקורות ({len(results)} מקורות)</h3>'

        # Show top 10 sources with full text
        for i, result in enumerate(results[:10], 1):
            metadata = result.metadata
            source_type = metadata.get('type', '')  # שיחה or מאמר
            seif = metadata.get('seif', metadata.get('perek', ''))
            farbrengen = metadata.get('farbrengen', '')
            sicha = metadata.get('sicha', '')
            maamar_type = metadata.get('maamar_type', '')

            # Build source title based on type
            if source_type == 'שיחה' and sicha:
                source_title = f"{sicha}"
            elif source_type == 'מאמר':
                # Extract דיבור המתחיל from chunk_title
                chunk_title = result.chunk_title
                if 'ד"ה' in chunk_title or 'דה' in chunk_title:
                    import re
                    match = re.search(r'(ד[״\"]ה[^/]+)', chunk_title)
                    if match:
                        source_title = match.group(1).strip()
                    else:
                        source_title = chunk_title.split('//')[-1].split('//')[0].strip()
                else:
                    source_title = chunk_title.split('//')[-1].strip()
            else:
                source_title = sicha or result.chunk_title

            sources_html += f'''
<details style="margin: 15px 0; padding: 15px; background: #fef9f3; border-radius: 8px; border-right: 3px solid #C79A51;">
<summary style="cursor: pointer; font-weight: bold; color: #1f2937; padding: 10px; font-size: 1.05rem;">
📜 מקור {i}: {source_title} • סעיף {seif}
</summary>
<div style="padding: 10px 0; margin-top: 10px;">
<p style="font-size: 0.9rem; color: #666; margin: 5px 0;"><strong>סוג:</strong> {source_type}{f' ({maamar_type})' if maamar_type else ''}</p>
<p style="font-size: 0.9rem; color: #666; margin: 5px 0;"><strong>ספר:</strong> {result.work}</p>
<p style="font-size: 0.9rem; color: #666; margin: 5px 0;"><strong>כותרת מלאה:</strong> {result.chunk_title}</p>
{f'<p style="font-size: 0.9rem; color: #666; margin: 5px 0;"><strong>פרבענגען:</strong> {farbrengen}</p>' if farbrengen else ''}
<div style="line-height: 1.9; font-family: 'Times New Roman', serif; font-size: 1.05rem; white-space: pre-wrap; border-top: 1px solid #e5e7eb; padding-top: 15px; margin-top: 10px;">
{result.text}
</div>
</div>
</details>
'''

        sources_html += '</div>'
        full_response = analysis + sources_html

        return jsonify({
            'success': True,
            'analysis': full_response,
            'result_count': len(results),
            'raw_results_count': len(results)
        })

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    sichos_file = Path(os.environ.get('SICHOS_FILE',
        'data/sichos.json' if Path('data/sichos.json').exists()
        else "/Users/elishapearl/Downloads/sichos_structured (4).json"))
    maamarim_file = Path(os.environ.get('MAAMARIM_FILE',
        'data/maamarim.json' if Path('data/maamarim.json').exists()
        else "/Users/elishapearl/Downloads/maamarim_structured (2).json"))

    sichos_exists = sichos_file.exists()
    maamarim_exists = maamarim_file.exists()

    return jsonify({
        'status': 'healthy',
        'sichos_accessible': sichos_exists,
        'maamarim_accessible': maamarim_exists,
        'dataset_accessible': sichos_exists and maamarim_exists,
        'environment': 'production' if os.environ.get('RAILWAY_ENVIRONMENT') else 'development'
    })

if __name__ == '__main__':
    # Create a simple launcher script
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
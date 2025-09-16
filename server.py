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
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        if not self.dataset_path.exists():
            raise ValueError(f"Dataset path does not exist: {dataset_path}")

    def search_term_in_files(self, search_term: str, max_files: int = 30) -> List[str]:
        """Search for files containing the search term using ripgrep"""
        try:
            cmd = [
                'rg', '-l', '--type', 'json',
                search_term, str(self.dataset_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                return [f for f in files if f.strip()][:max_files]
            else:
                logger.warning(f"ripgrep search failed: {result.stderr}")
                return []
        except subprocess.TimeoutExpired:
            logger.error("Search timeout")
            return []
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def extract_matching_chunks(self, file_path: str, search_term: str) -> List[SearchResult]:
        """Extract chunks containing the search term from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            results = []
            book_name = data.get('book_name_he', '') or data.get('book_name_en', '')
            author = self._determine_author(file_path, data)

            chunks = data.get('chunks', [])
            for chunk in chunks:
                text = chunk.get('text', '')
                if search_term in text:
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
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return []

    def _determine_author(self, file_path: str, data: Dict) -> str:
        """Determine the author based on file path and data"""
        path_str = str(file_path).lower()

        if 'alter rebbe' in path_str or 'admur hazaken' in path_str:
            return 'אדמו״ר הזקן'
        elif 'mitteler rebbe' in path_str:
            return 'אדמו״ר האמצעי'
        elif 'tzemach tzedek' in path_str:
            return 'הצמח צדק'
        elif 'rebbe rayatz' in path_str:
            return 'אדמו״ר הריי״צ'
        elif 'the rebbe' in path_str:
            return 'הרבי'
        else:
            # Try to determine from metadata
            author_he = data.get('book_metadata', {}).get('author_he', '')
            author_en = data.get('book_metadata', {}).get('author_en', '')
            return author_he or author_en or 'לא ידוע'

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

    def search_concept(self, search_term: str, context: str = '', max_results: int = 10) -> List[SearchResult]:
        """Main search function that finds and processes results"""
        logger.info(f"Searching for: {search_term}")

        # Find files containing the search term
        matching_files = self.search_term_in_files(search_term)
        logger.info(f"Found {len(matching_files)} files")

        # Extract matching chunks from each file
        all_results = []
        for file_path in matching_files:
            chunks = self.extract_matching_chunks(file_path, search_term)
            all_results.extend(chunks)

        # Sort by relevance and limit results
        # For now, simple sorting by text length (longer = more detailed)
        all_results.sort(key=lambda x: len(x.text), reverse=True)

        return all_results[:max_results]

class ChabadAnalyzer:
    def __init__(self, anthropic_api_key: str):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)

    def analyze_search_results(self, search_term: str, results: List[SearchResult],
                             context: str = '') -> str:
        """Use Claude to analyze search results and provide explanations"""

        # Prepare the results for analysis
        results_text = self._format_results_for_analysis(results)

        prompt = f"""You are an expert in Chabad Chassidic literature and Jewish mysticism.

I found the following texts related to "{search_term}" in the Chabad corpus:

{results_text}

{f"Additional context: {context}" if context else ""}

Please analyze these texts and provide:

1. **Overview**: A brief overview of how "{search_term}" is understood in Chabad Torah

2. **Main Explanations**: Identify and explain the 2-3 main approaches/explanations found in these texts, organized by:
   - The core concept
   - Key sources (with exact ד״ה discourse titles)
   - Brief explanation

3. **Analysis by Author**: How different Chabad leaders approached this concept

4. **Explanations in Three Languages**:
   - **Hebrew** (בעברית): Brief explanation in Hebrew
   - **Yiddish** (אויף יידיש): Brief explanation in Yiddish
   - **English**: Brief explanation in English

Format your response in clean HTML with proper Hebrew text direction and styling. Use RTL direction for Hebrew and Yiddish text.
"""

        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _format_results_for_analysis(self, results: List[SearchResult]) -> str:
        """Format search results for Claude analysis"""
        formatted = []

        for i, result in enumerate(results, 1):
            formatted.append(f"""
**Result {i}:**
- **Author**: {result.author}
- **Work**: {result.work}
- **Discourse Title**: {result.discourse_title}
- **Chunk Title**: {result.chunk_title}
- **Text**: {result.text[:1000]}{'...' if len(result.text) > 1000 else ''}

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
        dataset_path = data.get('dataset_path', '').strip()
        max_results = int(data.get('max_results', 10))
        anthropic_api_key = data.get('anthropic_api_key', '').strip()

        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        if not dataset_path:
            return jsonify({'error': 'Dataset path is required'}), 400

        if not anthropic_api_key:
            return jsonify({'error': 'Anthropic API key is required'}), 400

        # Initialize services
        global search_service, analyzer
        search_service = ChabadSearchService(dataset_path)
        analyzer = ChabadAnalyzer(anthropic_api_key)

        # Perform search
        results = search_service.search_concept(search_term, context, max_results)

        if not results:
            return jsonify({
                'success': True,
                'analysis': f'<p>No results found for "{search_term}" in the dataset.</p>'
            })

        # Analyze results with Claude
        analysis = analyzer.analyze_search_results(search_term, results, context)

        return jsonify({
            'success': True,
            'analysis': analysis,
            'result_count': len(results)
        })

    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Create a simple launcher script
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
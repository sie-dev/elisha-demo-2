#!/usr/bin/env python3
"""
Chabad Text Search Tool
A comprehensive search utility for Chabad literature collections
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SearchResult:
    """Container for search results"""
    file_path: str
    book_name: str
    chunk_id: int
    chunk_title: str
    match_text: str
    context_before: str
    context_after: str
    full_text: str

class ChabadTextSearch:
    """Main search class for Chabad texts"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.results = []

    def find_json_files(self) -> List[Path]:
        """Find all JSON files in the directory structure"""
        json_files = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(Path(root) / file)
        return sorted(json_files)

    def load_json_safely(self, file_path: Path) -> Optional[Dict[Any, Any]]:
        """Safely load JSON file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return None

    def clean_html_tags(self, text: str) -> str:
        """Remove HTML tags and clean up text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_context(self, text: str, match_pos: int, context_size: int = 200) -> Tuple[str, str]:
        """Extract context before and after the match"""
        start = max(0, match_pos - context_size)
        end = min(len(text), match_pos + context_size)

        before = text[start:match_pos].strip()
        after = text[match_pos:end].strip()

        return before, after

    def search_in_text(self, pattern: str, text: str, case_sensitive: bool = False,
                      whole_words: bool = False) -> List[Tuple[int, str]]:
        """Search for pattern in text and return matches with positions"""
        if not text:
            return []

        flags = 0 if case_sensitive else re.IGNORECASE

        if whole_words:
            # Add word boundaries for Hebrew and English
            pattern = r'\b' + pattern + r'\b'

        try:
            matches = []
            for match in re.finditer(pattern, text, flags):
                matches.append((match.start(), match.group()))
            return matches
        except re.error as e:
            print(f"Regex error: {e}")
            return []

    def search_file(self, file_path: Path, pattern: str, **search_options) -> List[SearchResult]:
        """Search within a single JSON file"""
        data = self.load_json_safely(file_path)
        if not data:
            return []

        results = []

        # Get book metadata
        book_name_he = data.get('book_name_he', '')
        book_name_en = data.get('book_name_en', '')
        book_name = f"{book_name_he} / {book_name_en}" if book_name_he and book_name_en else (book_name_he or book_name_en or str(file_path.name))

        # Search in chunks
        chunks = data.get('chunks', [])
        for chunk in chunks:
            chunk_text = chunk.get('text', '')
            chunk_title = chunk.get('chunk_title', '') or chunk.get('chunk_metadata', {}).get('chunk_title', '')
            chunk_id = chunk.get('chunk_id', 0)

            # Clean text for better searching
            clean_text = self.clean_html_tags(chunk_text)

            # Filter search options for search_in_text
            text_search_options = {k: v for k, v in search_options.items()
                                 if k in ['case_sensitive', 'whole_words']}

            # Search in the text
            matches = self.search_in_text(pattern, clean_text, **text_search_options)

            for match_pos, match_text in matches:
                context_before, context_after = self.extract_context(clean_text, match_pos)

                result = SearchResult(
                    file_path=str(file_path),
                    book_name=book_name,
                    chunk_id=chunk_id,
                    chunk_title=chunk_title,
                    match_text=match_text,
                    context_before=context_before,
                    context_after=context_after,
                    full_text=clean_text
                )
                results.append(result)

        return results

    def search_all(self, pattern: str, file_filter: str = "*", **search_options) -> List[SearchResult]:
        """Search across all files"""
        json_files = self.find_json_files()

        # Filter files if pattern provided
        if file_filter != "*":
            json_files = [f for f in json_files if file_filter.lower() in str(f).lower()]

        all_results = []
        total_files = len(json_files)

        for i, file_path in enumerate(json_files, 1):
            if search_options.get('verbose', False):
                print(f"Searching {i}/{total_files}: {file_path.name}")

            results = self.search_file(file_path, pattern, **search_options)
            all_results.extend(results)

        return all_results

    def format_results(self, results: List[SearchResult], max_results: int = None,
                      show_context: bool = True) -> str:
        """Format search results for display"""
        if not results:
            return "No results found."

        if max_results:
            results = results[:max_results]

        output = []
        output.append(f"Found {len(results)} result(s):\n")

        for i, result in enumerate(results, 1):
            output.append(f"=== Result {i} ===")
            output.append(f"Book: {result.book_name}")
            output.append(f"Section: {result.chunk_title}")
            output.append(f"File: {Path(result.file_path).name}")

            if show_context:
                output.append(f"\nMatch: '{result.match_text}'")
                if result.context_before:
                    output.append(f"Before: ...{result.context_before[-100:]}")
                if result.context_after:
                    output.append(f"After: {result.context_after[:100]}...")
            else:
                output.append(f"Match: '{result.match_text}'")

            output.append("-" * 50)

        return "\n".join(output)

    def export_results(self, results: List[SearchResult], output_file: str, format_type: str = "json"):
        """Export results to file"""
        output_path = Path(output_file)

        if format_type.lower() == "json":
            results_data = []
            for result in results:
                results_data.append({
                    'file_path': result.file_path,
                    'book_name': result.book_name,
                    'chunk_id': result.chunk_id,
                    'chunk_title': result.chunk_title,
                    'match_text': result.match_text,
                    'context_before': result.context_before,
                    'context_after': result.context_after
                })

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False, indent=2)

        elif format_type.lower() == "txt":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.format_results(results, show_context=True))

        print(f"Results exported to: {output_path}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Search through Chabad text collections")
    parser.add_argument("pattern", help="Search pattern (supports regex)")
    parser.add_argument("-p", "--path", default="/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads",
                       help="Base path to search")
    parser.add_argument("-f", "--filter", default="*", help="Filter files by name pattern")
    parser.add_argument("-c", "--case-sensitive", action="store_true", help="Case sensitive search")
    parser.add_argument("-w", "--whole-words", action="store_true", help="Match whole words only")
    parser.add_argument("-m", "--max-results", type=int, help="Maximum number of results to show")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-context", action="store_true", help="Don't show context around matches")
    parser.add_argument("-o", "--output", help="Export results to file")
    parser.add_argument("--format", choices=["json", "txt"], default="json",
                       help="Export format (json or txt)")

    args = parser.parse_args()

    # Validate path
    if not Path(args.path).exists():
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    # Create searcher and run search
    searcher = ChabadTextSearch(args.path)

    search_options = {
        'case_sensitive': args.case_sensitive,
        'whole_words': args.whole_words,
        'verbose': args.verbose
    }

    print(f"Searching for: '{args.pattern}'")
    print(f"Path: {args.path}")
    print(f"Filter: {args.filter}")
    print("-" * 50)

    results = searcher.search_all(args.pattern, args.filter, **search_options)

    # Display results
    show_context = not args.no_context
    formatted_output = searcher.format_results(results, args.max_results, show_context)
    print(formatted_output)

    # Export if requested
    if args.output:
        searcher.export_results(results, args.output, args.format)

if __name__ == "__main__":
    main()
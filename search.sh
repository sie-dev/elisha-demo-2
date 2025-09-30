#!/bin/bash

# Simple wrapper script for Chabad text search

BASE_PATH="/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEARCH_SCRIPT="$SCRIPT_DIR/chabad_text_search.py"

# Default settings
MAX_RESULTS=10
VERBOSE=""

# Show usage
show_usage() {
    echo "Chabad Text Search - Simple Usage"
    echo "Usage: $0 [OPTIONS] <search_term>"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -a, --all            Search all collections"
    echo "  -t, --toras-menachem Search only Toras Menachem"
    echo "  -r, --rebbe          Search all Rebbe's works"
    echo "  -z, --zohar          Search Zohar"
    echo "  -m, --max <n>        Maximum results (default: 10)"
    echo "  -c, --case-sensitive Case sensitive search"
    echo "  -w, --whole-words    Match whole words only"
    echo "  -v, --verbose        Verbose output"
    echo "  -o, --output <file>  Save results to file"
    echo ""
    echo "Examples:"
    echo "  $0 'לכתחילה אריבער'"
    echo "  $0 -t 'תשובה'"
    echo "  $0 -m 5 'שויתי ה׳ לנגדי'"
    echo "  $0 --output results.json 'אהבת ישראל'"
}

# Parse arguments
SEARCH_TERM=""
COLLECTION=""
OUTPUT_FILE=""
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -a|--all)
            COLLECTION=""
            shift
            ;;
        -t|--toras-menachem)
            COLLECTION="Toras Menachem"
            shift
            ;;
        -r|--rebbe)
            COLLECTION="The Rebbe"
            shift
            ;;
        -z|--zohar)
            COLLECTION="Zohar"
            shift
            ;;
        -m|--max)
            MAX_RESULTS="$2"
            shift 2
            ;;
        -c|--case-sensitive)
            EXTRA_ARGS="$EXTRA_ARGS --case-sensitive"
            shift
            ;;
        -w|--whole-words)
            EXTRA_ARGS="$EXTRA_ARGS --whole-words"
            shift
            ;;
        -v|--verbose)
            EXTRA_ARGS="$EXTRA_ARGS --verbose"
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            EXTRA_ARGS="$EXTRA_ARGS --output \"$2\""
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [[ -z "$SEARCH_TERM" ]]; then
                SEARCH_TERM="$1"
            else
                echo "Multiple search terms provided. Use quotes for phrases."
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if search term provided
if [[ -z "$SEARCH_TERM" ]]; then
    echo "Error: No search term provided"
    show_usage
    exit 1
fi

# Build command
CMD="python3 \"$SEARCH_SCRIPT\" \"$SEARCH_TERM\" -p \"$BASE_PATH\" -m $MAX_RESULTS"

if [[ -n "$COLLECTION" ]]; then
    CMD="$CMD -f \"$COLLECTION\""
fi

CMD="$CMD $EXTRA_ARGS"

# Show what we're doing
echo "Searching for: '$SEARCH_TERM'"
if [[ -n "$COLLECTION" ]]; then
    echo "Collection: $COLLECTION"
else
    echo "Collection: All"
fi
echo "Max results: $MAX_RESULTS"
echo "---"

# Execute search
eval $CMD
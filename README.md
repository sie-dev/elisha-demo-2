# Chabad Torah Search Interface

AI-powered search and analysis tool for Chabad Chassidic literature, featuring real-time dataset search with Claude Sonnet 4 integration.

## Features

- **Comprehensive Search**: Search through 75+ JSON files containing works from all Chabad leaders
- **AI-Powered Analysis**: Uses Claude AI to analyze and explain concepts in context
- **Multi-Language Support**: Provides explanations in Hebrew, Yiddish, and English
- **Source Attribution**: Shows exact discourse titles (ד״ה) and source information
- **Real-time Processing**: Fast search using ripgrep with intelligent filtering

## Replicates Our Analysis

This interface replicates the exact process we used to analyze בנין המלכות:

1. **File Discovery**: Uses `ripgrep` to find files containing the search term
2. **Chunk Extraction**: Extracts relevant text chunks with metadata
3. **AI Analysis**: Uses Claude to identify main explanations and provide multilingual summaries
4. **Source Attribution**: Maintains exact ד״ה titles and authorship information

## Setup Instructions

### Prerequisites

- Python 3.8+
- `ripgrep` (rg) installed on your system
- Claude API key from Anthropic
- Access to the Chabad uploads dataset

### Install ripgrep

**macOS:**
```bash
brew install ripgrep
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install ripgrep

# Other distributions
curl -LO https://github.com/BurntSushi/ripgrep/releases/download/13.0.0/ripgrep_13.0.0_amd64.deb
sudo dpkg -i ripgrep_13.0.0_amd64.deb
```

### Installation

1. **Clone/Download the files:**
   ```bash
   cd /Users/elishapearl/chabad_search_interface
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make the server executable:**
   ```bash
   chmod +x server.py
   ```

## Usage

### Option 1: Full Backend (Recommended)

1. **Start the Flask server:**
   ```bash
   python server.py
   ```

2. **Open your browser to:**
   ```
   http://localhost:5000
   ```

3. **Configure the interface:**
   - Enter your Claude API key
   - Set the dataset path (default: `/Users/elishapearl/Library/CloudStorage/Dropbox/chabad-uploads`)
   - Choose max results (5-20)

4. **Search and analyze:**
   - Enter a Hebrew or English search term
   - Add optional context
   - Click "Search Chabad Literature"

### Option 2: Frontend Only

Open `index.html` directly in your browser for a simpler version that makes direct API calls to Claude (requires CORS handling).

## Example Searches

- **בנין המלכות** - Building of Divine Kingship
- **יחודא עלאה ותתאה** - Upper and Lower Unity
- **אור וכלי** - Light and Vessels
- **עבודה בגשמיות** - Divine Service in Physicality
- **תיקון עולם** - Rectifying the World

## How It Works

### Backend Architecture

1. **Search Service** (`ChabadSearchService`):
   - Uses ripgrep for fast file searching
   - Extracts JSON chunks with metadata preservation
   - Determines authorship from file paths and metadata

2. **Analysis Service** (`ChabadAnalyzer`):
   - Formats search results for Claude analysis
   - Generates comprehensive explanations
   - Provides multilingual summaries

3. **Flask API**:
   - `/api/search` - Main search endpoint
   - `/api/health` - Health check
   - `/` - Serves the web interface

### Search Process

```
User Input → File Discovery (ripgrep) → Chunk Extraction →
Claude Analysis → Formatted Results → Web Display
```

## Configuration

### Environment Variables

- `PORT` - Server port (default: 5000)

### Dataset Structure Expected

The system expects JSON files in this structure:
```json
{
  "book_name_he": "ספר המאמרים מלוקט",
  "book_name_en": "Sefer HaMaamarim — Melukat",
  "chunks": [
    {
      "chunk_id": 1,
      "chunk_metadata": {
        "chunk_title": "...",
        "maamar": "ד\"ה יבחר לנו את נחלתינו תשכ\"ג",
        "seif": "א"
      },
      "text": "..."
    }
  ]
}
```

## Security Notes

- API keys are stored locally in browser localStorage
- API keys are only sent to Claude's servers for analysis
- No data is logged or stored on the server
- All processing is done locally except for Claude API calls

## Limitations

- Requires local access to the Chabad uploads dataset
- Claude API usage costs apply
- Search limited to exact term matches (not semantic search)
- Response time depends on dataset size and Claude API latency

## Troubleshooting

### "ripgrep not found" error
Install ripgrep using your package manager (see prerequisites)

### "Dataset path does not exist" error
Verify the path to your Chabad uploads directory and update in the interface

### "Claude API error" error
Check your API key and ensure it has sufficient credits

### Slow searches
- Reduce max results
- Use more specific search terms
- Ensure ripgrep is properly installed

## Technical Details

### Dependencies
- **Flask**: Web framework
- **anthropic**: Claude API client
- **ripgrep**: Fast text search
- **pathlib**: Path handling
- **json**: JSON processing

### Performance
- Typical search: 2-10 seconds
- File discovery: <1 second (ripgrep)
- Claude analysis: 5-30 seconds depending on complexity
- Memory usage: ~50MB for typical searches

## Future Enhancements

- Semantic search capabilities
- Result caching
- Export functionality
- Advanced filtering options
- Multi-term search queries
- Search history

---

**Created to replicate the comprehensive analysis process used for בנין המלכות research**
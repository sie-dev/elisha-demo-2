# AI חברותא - Unified Chat Interface
### Conversational AI for Sichos and Maamarim תשל״ה

A unified chat interface that combines search and conversation with AI-powered analysis of Chabad Chassidic texts. Ask questions, get comprehensive answers with full source texts, and engage in follow-up discussions - all in **Hebrew**, **Yiddish**, or **English**.

---

## 🎯 Features

### **💬 Unified Chat Experience**
- Single conversation interface for all interactions
- Ask questions naturally, search for concepts, or request explanations
- Full conversation history maintained for contextual follow-ups
- Beautiful, modern chat UI with smooth animations

### **🤖 Intelligent AI Analysis**
- Flowing, essay-style explanations (not bullet points)
- Comprehensive concept overviews
- Main ideas explained in natural language
- Tri-lingual explanations (Hebrew, Yiddish, English)
- Related concepts and connections
- Practical applications (למעשה)

### **📖 Complete Source Access**
- **Full chunk texts** included with every response
- Collapsible source sections with complete Hebrew text
- Exact citations (type, seif/perek, title)
- No truncation - see the entire source material
- Up to 10 most relevant sources per query

### **📚 Complete Corpus**
- 324 Sichos chunks from תשל״ה
- 80 Maamarim chunks from תשל״ה
- 404 total sources searchable

### **🌍 Multilingual**
- Query in Hebrew (עברית), Yiddish (אידיש), or English
- Smart language detection
- Natural conversation in your preferred language

---

## 📋 Prerequisites

- **Python 3.8+**
- **pip** (Python package installer)
- The two data files:
  - `/Users/elishapearl/Downloads/sichos_structured (4).json`
  - `/Users/elishapearl/Downloads/maamarim_structured (2).json`

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install flask flask-cors anthropic
```

### 2. Run the Server

```bash
cd /Users/elishapearl/chabad_search_interface
./run.sh
```

Or run directly:

```bash
python3 server.py
```

### 3. Open in Browser

Navigate to: **http://localhost:8080**

---

## 📖 Usage Examples

Just type naturally in the chat! The AI understands:

### **Questions**
- `מה זה "משתשקע החמה"?`
- `הסבר את הקשר בין שבת וחנוכה`
- `What is malchus according to the Rebbe?`

### **Concept Searches**
- `בת ציון`
- `מלכות`
- `אתהפכא`

### **Follow-up Questions**
After getting an answer, you can ask:
- `תן לי עוד דוגמאות`
- `מה הקשר לחסידות?`
- `Can you explain that in simpler terms?`

### **Try the Suggestion Chips**
Click any suggestion on the welcome screen to start:
- "מה זה משתשקע החמה?"
- "הקשר בין שבת וחנוכה"
- "מה זו בת ציון?"

---

## 🏗️ Architecture

### Backend (Flask)
- **`server.py`**: Main Flask application
  - `ChabadSearchService`: Loads and searches JSON files
  - `ChabadAnalyzer`: Interfaces with Claude AI for analysis
  - API endpoints:
    - `/api/health`: Check server and data file status
    - `/api/search`: Search and analyze texts

### Frontend (HTML/JavaScript)
- **`index.html`**: Single-page application
  - Search panel: Direct text search
  - Chat panel: Conversational AI interface
  - Real-time server status indicator

### Data Format

The JSON files contain structured Chabad texts with chunks for easy searching and retrieval.

---

## 🔧 Configuration

### API Key

The system includes a hardcoded Anthropic API key for AI analysis. To use your own key:

1. Open `index.html`
2. Find the `anthropic_api_key` field in the fetch calls
3. Replace with your API key

Or set as demo mode by using `"demo_key"` (shows raw results without AI analysis).

### File Paths

To use different JSON files, edit `server.py`:

```python
sichos_file = "/path/to/your/sichos.json"
maamarim_file = "/path/to/your/maamarim.json"
```

### Port

Default port is **8080**. To change, edit `server.py` and `index.html`.

---

## 🧪 Testing

Run the test script to verify functionality:

```bash
python3 test_search.py
```

This tests Hebrew search terms and system responsiveness.

---

## 🐛 Troubleshooting

### Server Won't Start

**Error: "Address already in use"**
- On macOS, disable AirPlay Receiver in System Preferences
- Or use a different port: `PORT=8081 python3 server.py`

### Files Not Found

Verify the file paths in `server.py` and check that the JSON files exist.

### No Search Results

- Verify search term spelling
- Try broader terms (e.g., "שבת" instead of "שבת קודש")
- Check server logs

---

## 📧 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the server logs
3. Test with `test_search.py`

---

**בהצלחה! Good luck with your learning!**
# 🚀 Quick Setup Guide

## For New Users

### 1. Clone the Repository
```bash
git clone https://github.com/sie-dev/elisha-demo-2.git
cd elisha-demo-2
```

### 2. Set Up Your API Key
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use any text editor
```

Add this line to `.env`:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Prepare Data Files

Place these two JSON files in `/Users/YOUR_USERNAME/Downloads/`:
- `sichos_structured (4).json`
- `maamarim_structured (2).json`

Or update the file paths in `server.py` lines 434-435:
```python
sichos_file = "/path/to/your/sichos_structured (4).json"
maamarim_file = "/path/to/your/maamarim_structured (2).json"
```

### 4. Install Dependencies
```bash
pip3 install flask flask-cors anthropic
```

### 5. Run the Server
```bash
./run.sh
```

Or manually:
```bash
export ANTHROPIC_API_KEY="your_key_here"
python3 server.py
```

### 6. Open in Browser
Navigate to: **http://localhost:8080**

---

## For Sharing / Deployment

### Environment Variables
Always use environment variables for sensitive data:

```bash
# Local development
export ANTHROPIC_API_KEY="sk-ant-..."

# Or create .env file (never commit this!)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### Deploy to Cloud

**Railway / Render / Heroku:**
1. Add `ANTHROPIC_API_KEY` as environment variable in dashboard
2. Upload your JSON data files
3. Update file paths in `server.py`
4. Deploy!

**GitHub Pages** (Frontend only):
- Won't work fully as GitHub Pages doesn't support Python backend
- Consider using Railway for backend + GitHub Pages for static demo

---

## Troubleshooting

### API Key Not Working
- Make sure `.env` file exists in the project root
- Verify the key starts with `sk-ant-`
- Check that server is loading the environment variable

### Files Not Found
- Verify JSON files exist at the specified paths
- Check server logs for exact error messages

### Server Won't Start
- Port 8080 in use? Try: `PORT=8081 python3 server.py`
- Missing dependencies? Run: `pip3 install flask flask-cors anthropic`

---

**Need help?** Check the main README.md or open an issue on GitHub!
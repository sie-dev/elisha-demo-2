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

### **Option 1: GitHub Pages (FREE) ⭐ RECOMMENDED**

The site is already configured for GitHub Pages!

**Steps:**
1. Go to your repo: https://github.com/sie-dev/elisha-demo-2
2. Settings → Pages
3. Source: Deploy from branch `gh-pages`
4. Click Save

Your site will be live at: **https://sie-dev.github.io/elisha-demo-2/**

**Note:** You still need the backend deployed separately (see Option 2).

---

### **Option 2: Deploy Backend to Railway**

**Quick Deploy:**
1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub"
3. Select `sie-dev/elisha-demo-2`
4. Add environment variable: `ANTHROPIC_API_KEY=your_key`
5. Upload your JSON files to Railway or use S3/URL
6. Update `server.py` with JSON file paths

Railway will give you a URL like: `https://your-app.up.railway.app`

**Update the frontend:**
Edit `index.html` line 533 with your Railway URL.

---

### **Option 3: Full Local Deployment**

```bash
# Local development
export ANTHROPIC_API_KEY="sk-ant-..."
python3 server.py

# Open in browser
http://localhost:8080
```

---

### **Complete Setup (GitHub Pages + Railway)**

1. **Backend on Railway:**
   - Deploy `server.py`
   - Add API key to environment
   - Upload JSON files
   - Get Railway URL

2. **Frontend on GitHub Pages:**
   - Already configured!
   - Auto-detects Railway backend
   - Enable in GitHub Settings → Pages

3. **Result:**
   - Public site: `https://sie-dev.github.io/elisha-demo-2/`
   - Backend: `https://your-app.up.railway.app`
   - Works together automatically!

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
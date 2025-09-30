# 🚂 Railway Deployment Guide

## Quick Deploy (5 minutes)

### **Step 1: Create Railway Project**

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `sie-dev/elisha-demo-2`

### **Step 2: Upload Data Files**

You need to upload your two JSON files to Railway. **Two options:**

#### **Option A: Use Railway Volumes (RECOMMENDED)**

1. In Railway dashboard, go to your service
2. Click "Variables" tab
3. Add these variables:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   SICHOS_FILE=/app/data/sichos.json
   MAAMARIM_FILE=/app/data/maamarim.json
   ```

4. Go to "Settings" → "Volumes"
5. Create a volume mounted at `/app/data`
6. Upload your files via Railway CLI or use the web interface:
   - Upload `/Users/elishapearl/Downloads/sichos_structured (4).json` as `/app/data/sichos.json`
   - Upload `/Users/elishapearl/Downloads/maamarim_structured (2).json` as `/app/data/maamarim.json`

#### **Option B: Embed in Repository (If files are small)**

1. Copy files to repo:
   ```bash
   mkdir -p data
   cp "/Users/elishapearl/Downloads/sichos_structured (4).json" data/sichos.json
   cp "/Users/elishapearl/Downloads/maamarim_structured (2).json" data/maamarim.json
   ```

2. Update `server.py` line 434-435:
   ```python
   sichos_file = "data/sichos.json"
   maamarim_file = "data/maamarim.json"
   ```

3. Commit and push:
   ```bash
   git add data/ server.py
   git commit -m "Add data files for Railway"
   git push
   ```

### **Step 3: Configure Environment Variables**

In Railway dashboard → Your service → Variables:

**Required:**
```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Optional (if using volumes):**
```
SICHOS_FILE=/app/data/sichos.json
MAAMARIM_FILE=/app/data/maamarim.json
```

### **Step 4: Deploy**

Railway will automatically deploy! You'll get a URL like:
```
https://your-app-name.up.railway.app
```

### **Step 5: Update Frontend**

Copy your Railway URL and update `index.html`:

```javascript
// Line 467 and 533
const API_URL = window.location.hostname === 'localhost'
    ? 'http://localhost:8080'
    : 'https://YOUR-ACTUAL-RAILWAY-URL.up.railway.app';
```

Then commit and push:
```bash
git add index.html
git commit -m "Update Railway backend URL"
git push origin gh-pages
```

---

## 🔒 **No API Key Required from Users**

The API key is stored in Railway environment variables, so users **never** need to enter it!

The frontend sends `anthropic_api_key: 'USE_SERVER_KEY'` and the server uses:
```python
anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY', ...)
```

---

## ✅ **Testing Your Deployment**

Once deployed, test:

```bash
curl https://your-app.up.railway.app/api/health
```

Should return:
```json
{
  "status": "healthy",
  "dataset_accessible": true,
  "sichos_accessible": true,
  "maamarim_accessible": true
}
```

---

## 🎯 **Final Result**

- **Frontend:** https://sie-dev.github.io/elisha-demo-2/ (GitHub Pages - FREE)
- **Backend:** https://your-app.up.railway.app (Railway - FREE tier)
- **Users:** Just visit the site and start chatting - no API key needed!

---

## 🐛 **Troubleshooting**

### Files not found on Railway
- Check the file paths in environment variables
- Verify files were uploaded correctly
- Check Railway logs: `railway logs`

### API key not working
- Verify it's set in Railway environment variables
- Check it starts with `sk-ant-`
- Restart the Railway service after adding variables

---

**Ready to deploy?** Start at https://railway.app/new and follow Step 1!
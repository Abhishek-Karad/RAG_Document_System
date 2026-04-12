# Complete Setup Guide - Document QA System with Gemini LLM

Complete step-by-step instructions to get your Document QA system running with Gemini AI integration.

## 🎯 What You'll Build

A **production-ready document question-answering system** that:
- ✅ Accepts PDF, TXT, and other document uploads
- ✅ Automatically chunks documents for context
- ✅ Generates embeddings for semantic search
- ✅ Uses FAISS for lightning-fast similarity search
- ✅ **Uses Google Gemini LLM to formulate intelligent answers**
- ✅ Provides a beautiful React web interface

## 📋 Prerequisites (5 minutes)

### 1. Python & Node.js
```bash
# Check Python version (3.9+)
python --version

# Check Node.js version (16+)
node --version
npm --version
```

If missing, install from:
- Python: https://python.org
- Node.js: https://nodejs.org

### 2. Get Gemini API Key (2 minutes)
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key to a safe place
4. **You'll need this later!**

## 🚀 Backend Setup (10 minutes)

### Step 1: Install Python Dependencies
```bash
# Navigate to project root
cd FAISS_Backend-main

# Install required packages
pip install -r requirements.txt
```

**What's installed:**
- `fastapi` - Web framework
- `uvicorn` - Web server
- `faiss-cpu` - Vector similarity search
- `sentence-transformers` - Embedding generation
- `pypdf` - PDF parsing
- `google-generativeai` - Gemini LLM integration
- Plus 5+ other supporting packages

### Step 2: Create Uploads Directory
```bash
mkdir -p uploads
```

This folder stores uploaded documents and the FAISS index.

### Step 3: Set Gemini API Key
```bash
# Option A: Export as environment variable (this session only)
export GEMINI_API_KEY="your-gemini-api-key-here"

# Option B: Create .env file (persistent)
echo 'GEMINI_API_KEY=your-gemini-api-key-here' > .env
```

### Step 4: Start Backend Server
```bash
python main.py
```

**Expected output:**
```
✓ FAISS Index loaded
✓ Gemini API configured successfully
✓ Uvicorn running on http://0.0.0.0:7999

INFO:     Uvicorn running on http://0.0.0.0:7999 (Press CTRL+C to quit)
```

### ✅ Backend Running!
- API URL: http://localhost:7999
- Docs: http://localhost:7999/docs
- Health: http://localhost:7999/health

**Keep this terminal open!** Open a new terminal for the next steps.

---

## 🎨 Frontend Setup (5 minutes)

### Step 1: Navigate to Frontend
```bash
cd frontend
```

### Step 2: Install Node Dependencies
```bash
npm install
```

**What's installed:**
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- Lucide React (icons)
- Axios (HTTP client)

### Step 3: Configuration (Optional)
If your backend is **not** on `localhost:7999`, create `.env`:
```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:7999
```

### Step 4: Start Development Server
```bash
npm run dev
```

**Expected output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### ✅ Frontend Running!
- Web App: http://localhost:5173
- Frontend dev server running

---

## 📖 Using Your Document QA System

### 1. Open the Web App
Visit: **http://localhost:5173**

You'll see:
- 📄 **Upload Documents** tab
- 📋 **Your Documents** tab
- ❓ **Ask Questions** tab

### 2. Upload a Document

1. Click **"Upload Documents"** tab
2. **Drag & drop** a PDF or text file, or click to browse
3. Wait for success message
4. Document appears in **"Your Documents"** list

**Supported formats:**
- `.pdf` - PDF documents
- `.txt` - Text files
- `.md` - Markdown files

**Example files to test:**
```bash
# Create a sample document
echo "
Python is a programming language.
It's known for simplicity and readability.
Popular for data science, web development, and automation.
" > sample.txt
```

### 3. Ask a Question (With AI!)

1. Click **"Ask Questions"** tab
2. Type your question: `"What is Python?"`
3. **Enable checkbox**: "✓ Use AI to formulate answer"
4. Click **Send** or press Enter
5. Wait 2-5 seconds for response

**You'll see:**
```
🌟 AI Answer
─────────────────────────────────────
Based on the documents, Python is...
[AI-generated comprehensive answer]

3 Supporting Document Chunks
#1 sample.txt - Chunk 1 | Relevance: 95%
   [Click to expand]
...
```

### 4. Try Different Modes

**With AI Enabled (Checked):**
- Calls `/ask-llm` endpoint
- Gets comprehensive AI answer
- Shows supporting chunks
- Better for "summarize", "explain", "what is..." queries

**With AI Disabled (Unchecked):**
- Calls `/ask` endpoint
- Shows raw chunks only
- Faster response
- Good for "find specific text" queries

### 5. Adjust Parameters

**Top-K** (Default: 3)
- Number of document chunks to retrieve
- Higher = more context but slower
- Typical range: 1-5

**Threshold** (Default: 0.50)
- Minimum similarity score (0.0-1.0)
- Higher = only very similar chunks
- Lower = more results but lower quality

**Example combinations:**
```
Quick answers:     top_k=2, threshold=0.60
Thorough search:   top_k=5, threshold=0.40
Balanced:          top_k=3, threshold=0.50
```

---

## 🔌 API Endpoints Reference

### Upload & Manage Documents

```bash
# Upload a document
curl -X POST "http://localhost:7999/upload" \
  -F "file=@sample.pdf"

# List all documents
curl "http://localhost:7999/documents"

# Delete a document
curl -X DELETE "http://localhost:7999/documents/doc-id-here"
```

### Ask Questions

```bash
# Search with chunks only (no AI)
curl -X POST "http://localhost:7999/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "top_k": 3,
    "similarity_threshold": 0.50
  }'

# Ask with Gemini AI answer (NEW!)
curl -X POST "http://localhost:7999/ask-llm" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "top_k": 3,
    "similarity_threshold": 0.50,
    "model": "gemini-pro"
  }'
```

### System Info

```bash
# Health check
curl "http://localhost:7999/health"

# Statistics
curl "http://localhost:7999/stats"

# API Documentation (Interactive)
# Visit: http://localhost:7999/docs
```

---

## ⚙️ Advanced Configuration

### Change Server Port

```bash
# Start on different port
PORT=8000 python main.py

# Or in .env file
echo "PORT=8000" > .env
```

### Change Gemini Model

In `.env`:
```
GEMINI_MODEL=gemini-pro    # Default
# Or other models like gemini-pro-vision (if available)
```

### Custom Prompt for AI

Edit `faiss_manager.py`, find `generate_answer()` method:

```python
prompt = f"""You are a helpful assistant. Answer based ONLY on:
[Your custom instructions here]
Document Excerpts:
{context}

Question: {query}

Answer:"""
```

### Adjust Chunking Size

Edit `faiss_manager.py`, find `chunk_text()` method:

```python
def chunk_text(self, text, size=500, overlap=100):
    # size=500 (default) - characters per chunk
    # overlap=100 (default) - overlapping characters
```

Recommendations:
- **Larger docs**: size=800, overlap=150
- **Smaller docs**: size=300, overlap=50
- **Dense text**: size=350, overlap=75

---

## 🧪 Testing the System

### Test 1: Upload & Search (No AI)

```bash
# Create test document
cat > test.txt << 'EOF'
FAISS stands for Facebook AI Similarity Search.
It's a library for efficient similarity search.
FAISS is written in C++ with Python bindings.
EOF

# Upload (use web UI or API)
curl -X POST "http://localhost:7999/upload" \
  -F "file=@test.txt"

# Ask (without AI)
curl -X POST "http://localhost:7999/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is FAISS?","top_k":3,"similarity_threshold":0.5}'
```

### Test 2: AI Answer

```bash
# Ask with AI
curl -X POST "http://localhost:7999/ask-llm" \
  -H "Content-Type: application/json" \
  -d '{
    "question":"What is FAISS?",
    "top_k":3,
    "similarity_threshold":0.5,
    "model":"gemini-pro"
  }'
```

**Expected AI Response:**
```json
{
  "question": "What is FAISS?",
  "answer": "FAISS (Facebook AI Similarity Search) is a library designed for efficient similarity search and clustering of dense vectors. It's primarily written in C++ with Python bindings for easy integration...",
  "supporting_chunks": [...]
}
```

---

## 🐳 Docker Deployment (Optional)

### Run Everything with Docker Compose

```bash
# Start both backend and frontend
docker-compose up

# In browser: http://localhost:5173
```

### Manual Docker Build

```bash
# Build backend
docker build -t faiss-backend .
docker run -p 7999:7999 -e GEMINI_API_KEY=your-key faiss-backend

# Build frontend
cd frontend
docker build -t faiss-frontend .
docker run -p 5173:5173 faiss-frontend
```

---

## 🐛 Troubleshooting

### Backend Issues

**Error: "Port 7999 already in use"**
```bash
# Use different port
PORT=8000 python main.py
```

**Error: "GEMINI_API_KEY not configured"**
```bash
# Set the key
export GEMINI_API_KEY="your-actual-key"
python main.py

# Or in .env
echo "GEMINI_API_KEY=your-key" > .env
```

**Error: "Could not import google.generativeai"**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Error: "ModuleNotFoundError: No module named 'pypdf'"**
```bash
# pypdf should be installed, but if not:
pip install pypdf>=3.0.0
```

### Frontend Issues

**Error: "Cannot reach backend"**
- ✓ Backend running?
- ✓ Check http://localhost:7999/health
- ✓ Update VITE_API_URL in .env if needed

**AI Answer not working**
- ✓ Set GEMINI_API_KEY on backend
- ✓ Check backend logs for errors
- ✓ Verify API key is valid

**Slow page loads**
- ✓ Clear browser cache: Ctrl+Shift+Delete
- ✓ Check network tab in DevTools
- ✓ First LLM request ~3-5 seconds (normal)

---

## 📊 System Performance

### Typical Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| Upload PDF (1MB) | 0.5-2s | Depends on text length |
| Search chunks | 50-100ms | Ultra-fast FAISS |
| Generate AI answer | 2-5s | Gemini API latency |
| Full pipeline | 3-6s | Upload + Search + AI |

### Resource Usage

| Component | RAM | Disk |
|-----------|-----|------|
| SentenceTransformer model | 200MB | 350MB |
| FAISS index (1000 chunks) | 50-100MB | 150-200MB |
| Python runtime | 50MB | 10MB |
| Node.js (dev) | 100MB | 500MB |
| **Total** | **400-500MB** | **1GB** |

---

## 🔒 Security Notes

### For Development
- ✓ Local only (no internet exposure)
- ✓ API keys in .env (not committed)
- ✓ File uploads to local `uploads/` folder

### For Production
- 🔐 Use HTTPS only
- 🔐 Set CORS origins to your domain
- 🔐 Secure API key storage (AWS Secrets, etc)
- 🔐 Rate limiting on endpoints
- 🔐 Authentication/authorization layer
- 🔐 Virus scanning on uploads
- 🔐 Backup and disaster recovery

---

## 📚 Next Steps

### 1. Explore Features
- [ ] Upload multiple documents
- [ ] Try different questions
- [ ] Adjust top_k and threshold
- [ ] Toggle AI on/off
- [ ] Check API docs at /docs

### 2. Customize
- [ ] Adjust chunking parameters
- [ ] Modify AI prompt
- [ ] Change embedding model
- [ ] Style frontend with your colors

### 3. Integrate
- [ ] Embed web UI in your app
- [ ] Call API from your backend
- [ ] Build custom UI for your needs
- [ ] Add authentication

### 4. Deploy
- [ ] Move to server/cloud
- [ ] Set up reverse proxy (nginx)
- [ ] Enable HTTPS
- [ ] Monitor performance
- [ ] Set up backups

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| `README_NEW.md` | Feature overview |
| `LLM_INTEGRATION.md` | Gemini setup & configuration |
| `FRONTEND_SETUP.md` | React app details |
| `DEPLOYMENT.md` | Production deployment |
| `QUICK_START.md` | 5-minute setup |

---

## ❓ FAQ

**Q: Can I use different Gemini models?**  
A: Yes, change `model="gemini-pro"` to another available model. Keep the default for best results.

**Q: What if I don't want to use AI?**  
A: Just uncheck "Use AI" option. The /ask endpoint works without Gemini.

**Q: Can I increase similarity threshold to reduce results?**  
A: Yes, higher threshold (0.6-0.8) = stricter matching. Lower (0.3-0.5) = broader search.

**Q: How big can documents be?**  
A: Tested up to 50MB. Larger documents take longer but should work.

**Q: Can I use this offline?**  
A: Backend works offline. Gemini requires internet for LLM features.

---

## 🎉 You're All Set!

Your Document QA system is ready. Here's what to do now:

1. **Open browser**: http://localhost:5173
2. **Upload a document**: Try a PDF or text file
3. **Ask a question**: Enable AI and get answers!
4. **Share with friends**: Show them AI-powered answers!

---

**Questions or Issues?**

1. Check the troubleshooting section above
2. Review the detailed documentation files
3. Check backend logs: `python main.py` output
4. Verify all requirements are installed

**Happy questioning!** 🚀

---

**Made with ❤️ using FastAPI, FAISS, React, and Google Gemini**

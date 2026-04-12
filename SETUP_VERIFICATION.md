# ✅ Setup Verification Checklist

Use this checklist to verify your Document QA system with Gemini AI is properly configured.

## 📸 Before You Start

Make sure you have:
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed
- [ ] Gemini API key from https://makersuite.google.com/app/apikey
- [ ] 2GB+ free RAM
- [ ] Internet connection (for Gemini API)

---

## 🔧 Backend Setup Verification

### Step 1: Install Dependencies
```bash
cd FAISS_Backend-main
pip install -r requirements.txt
```

**Verify:**
- [ ] No errors during installation
- [ ] All packages downloaded successfully

**Check installed packages:**
```bash
pip list | grep -E "google-generativeai|faiss|sentence|pypdf|fastapi"
```

Should show:
```
fastapi (0.100+)
google-generativeai (0.3.0+)
pypdf (3.0+)
sentence-transformers (2.6+)
faiss-cpu (1.7+)
```

### Step 2: Create Required Directories
```bash
mkdir -p uploads
```

**Verify:**
- [ ] `uploads` directory exists
- [ ] Directory is empty or contains previous data

### Step 3: Set Gemini API Key

**Option A: Environment Variable (Current Session)**
```bash
export GEMINI_API_KEY="paste-your-key-here"
echo $GEMINI_API_KEY  # Should show your key
```

**Option B: .env File (Permanent)**
```bash
echo 'GEMINI_API_KEY=paste-your-key-here' > .env
cat .env  # Should show your key
```

**Verify:**
- [ ] API key is set (echo output shows key)
- [ ] Key starts with "AIza" (typical Google API format)
- [ ] No extra spaces or quotes around key

### Step 4: Start Backend Server
```bash
python main.py
```

**Wait for output:**
```
INFO:     Uvicorn running on http://0.0.0.0:7999
```

**Verify in logs:**
- [ ] "FAISS Index loaded" ✓
- [ ] "Gemini API configured successfully" ✓
- [ ] "Uvicorn running on http://0.0.0.0:7999" ✓
- [ ] No errors or warnings

### Step 5: Test Backend Health

**In a new terminal:**
```bash
curl http://localhost:7999/health
```

**Expected response:**
```json
{"status": "healthy"}
```

**Verify:**
- [ ] Health check returns status
- [ ] No connection errors

### Step 6: Check API Documentation
Visit: **http://localhost:7999/docs**

**Verify:**
- [ ] Page loads (Swagger UI)
- [ ] Lists all endpoints:
  - `POST /upload`
  - `GET /documents`
  - `POST /ask`
  - `POST /ask-llm` ← NEW!
  - `GET /stats`
  - etc.
- [ ] Interactive endpoint browser available

### Step 7: Test /ask Endpoint (No AI)

```bash
# First, upload a test file
echo "Python is a programming language" > test.txt

curl -X POST "http://localhost:7999/upload" \
  -F "file=@test.txt"
```

**Expected response:**
```json
{"id": "...", "filename": "test.txt", "num_chunks": 1}
```

**Verify:**
- [ ] File uploads successfully
- [ ] Document ID returned
- [ ] No upload errors

### Step 8: Test /ask-llm Endpoint (With AI)

```bash
curl -X POST "http://localhost:7999/ask-llm" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "top_k": 3,
    "similarity_threshold": 0.5,
    "model": "gemini-pro"
  }'
```

**Expected response:**
```json
{
  "question": "What is Python?",
  "answer": "Python is a high-level, interpreted programming language...",
  "supporting_chunks": [...],
  "chunk_count": 1
}
```

**Verify:**
- [ ] Request succeeds (status 200)
- [ ] Answer is not empty
- [ ] Answer mentions Python
- [ ] Supporting chunks included
- [ ] No errors in response

---

## 🎨 Frontend Setup Verification

### Step 1: Navigate to Frontend
```bash
# In a new terminal (keep backend running)
cd frontend
```

**Verify:**
- [ ] Directory contains package.json
- [ ] Can list files with `ls -la`

### Step 2: Install Dependencies
```bash
npm install
```

**Verify:**
- [ ] Installation completes (may take 1-2 min)
- [ ] `node_modules/` directory created
- [ ] No critical errors (warnings OK)

### Step 3: Check Configuration (Optional)
```bash
# If not at localhost:7999, create .env
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:7999
```

**Verify:**
- [ ] Backend URL is correct
- [ ] File saved

### Step 4: Start Development Server
```bash
npm run dev
```

**Expected output:**
```
VITE v4.x.x ready in xxx ms
Local: http://localhost:5173/
```

**Verify:**
- [ ] Server starts without errors
- [ ] Local URL shown as http://localhost:5173
- [ ] No port conflicts

### Step 5: Open in Browser
Visit: **http://localhost:5173**

**Verify:**
- [ ] Page loads (not blank)
- [ ] Title shows "Document QA System" or similar
- [ ] See 3 tabs: Upload, Documents, Ask Questions
- [ ] No console errors (F12 → Console)

### Step 6: Test Upload Feature
1. Click "Upload Documents" tab
2. Drag a PDF or TXT file (or create test.txt)
3. Wait for success message

**Verify:**
- [ ] Can select file
- [ ] Upload completes without error
- [ ] Success message appears
- [ ] No network errors in DevTools

### Step 7: Verify Document Shows Up
1. Click "Your Documents" tab

**Verify:**
- [ ] Uploaded document listed
- [ ] Shows filename and number of chunks
- [ ] Delete button present

### Step 8: Test Question Feature (With AI)
1. Click "Ask Questions" tab
2. **Check box:** "✓ Use AI to formulate answer" (default ON)
3. Type: "What is in the documents?"
4. Click Send

**Expected:**
- Response in 2-5 seconds
- Show "🌟 AI Answer" section with answer
- Show "Supporting Document Chunks" below

**Verify:**
- [ ] Question input works
- [ ] AI toggle is visible and checked by default
- [ ] Send button works
- [ ] Answer appears in formatted box
- [ ] Supporting chunks show below
- [ ] No error messages

### Step 9: Test Question Feature (Without AI)
1. **Uncheck box:** "☐ Use AI to formulate answer"
2. Type: "What is in the documents?"
3. Click Send

**Expected:**
- Response in <100ms (very fast)
- Show raw chunks with similarity scores
- No formatted answer

**Verify:**
- [ ] Toggle can be unchecked
- [ ] Fast response when AI off
- [ ] Chunks display correctly
- [ ] Similarity scores shown (e.g., "87%")

---

## 🔌 Integration Verification

### Full End-to-End Test

**Do this to verify everything works together:**

1. **Start Backend**
```bash
cd FAISS_Backend-main
export GEMINI_API_KEY=your-key
python main.py
```
- [ ] Backend running on :7999

2. **Start Frontend**
```bash
cd FAISS_Backend-main/frontend
npm run dev
```
- [ ] Frontend running on :5173

3. **Test Complete Flow**
```
Create test file with content
  ↓
Upload via http://localhost:5173
  ↓
Check "Your Documents" tab
  ↓
Go to "Ask Questions" tab
  ↓
Enable AI toggle ✓
  ↓
Ask a question
  ↓
See AI answer + supporting chunks
  ↓
Success! ✅
```

**Final Verify:**
- [ ] AI answer appears promptly
- [ ] Answer is coherent and relevant
- [ ] Supporting chunks shown with scores
- [ ] No errors anywhere

---

## 🐛 Diagnostic Commands

If something's wrong, run these:

### Check Python
```bash
python --version  # Should be 3.9+
```

### Check Node
```bash
node --version    # Should be 16+
npm --version     # Should be 8+
```

### Check Gemini Key
```bash
echo $GEMINI_API_KEY  # Should show your key starting with "AIza"
```

### Check Backend Logs
```bash
# Watch for:
# ✓ FAISS Index loaded
# ✓ Gemini API configured successfully
# ✓ Uvicorn running on...
```

### Check Frontend Network
```
F12 → Network tab
Perform a request
Check for 200 status codes
```

### Test API Directly
```bash
# Health
curl http://localhost:7999/health

# Stats
curl http://localhost:7999/stats

# List documents
curl http://localhost:7999/documents

# Ask (chunks only)
curl -X POST http://localhost:7999/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"test?"}'

# Ask with AI
curl -X POST http://localhost:7999/ask-llm \
  -H "Content-Type: application/json" \
  -d '{"question":"test?"}'
```

---

## 🎯 Success Criteria

### ✅ Backend is Working
- [ ] python main.py starts without errors
- [ ] "Gemini API configured successfully" in logs
- [ ] http://localhost:7999/health returns 200
- [ ] http://localhost:7999/docs loads
- [ ] /ask endpoint works (returns chunks)
- [ ] /ask-llm endpoint works (returns answer)

### ✅ Frontend is Working
- [ ] npm run dev starts without errors
- [ ] http://localhost:5173 loads
- [ ] Can see all 3 tabs
- [ ] Upload interface displays
- [ ] Can select and upload files
- [ ] "Use AI to formulate answer" toggle visible
- [ ] Can type questions
- [ ] Can toggle AI on/off

### ✅ Full System Working
- [ ] Upload document successfully
- [ ] Document appears in list
- [ ] Ask question with AI ON → get answer
- [ ] Ask question with AI OFF → get chunks
- [ ] Toggle between modes works
- [ ] No errors in console or logs
- [ ] Response times reasonable (<10 seconds)

---

## 📋 Troubleshooting Quick Reference

| Issue | Check | Fix |
|-------|-------|-----|
| Backend not starting | Python version | `python --version` → 3.9+ |
| Missing packages | Installation | `pip install -r requirements.txt` |
| Gemini API error | API key | `export GEMINI_API_KEY=your-key` |
| Connection refused | Backend port | Is `python main.py` running? |
| Frontend not starting | Node version | `node --version` → 16+ |
| Can't reach backend | Network config | Check VITE_API_URL in .env |
| No AI answer | API key set? | Export GEMINI_API_KEY and restart |
| Slow responses | Parameters | Reduce top_k, increase threshold |
| Old results showing | Cache | F12 → Clear storage |

---

## 📞 Getting Help

If something doesn't work:

1. **Check this list again** - Most issues covered
2. **Read detailed guides**:
   - COMPLETE_SETUP.md - Full setup guide
   - LLM_INTEGRATION.md - AI-specific help
   - FRONTEND_SETUP.md - Frontend details
3. **Check logs** - Backend and frontend console
4. **Verify prerequisites** - Python, Node, API key
5. **Test individually** - Backend first, then frontend

---

## 🎉 When Everything Works

You'll see:
```
✅ Backend: "Uvicorn running on http://0.0.0.0:7999"
✅ Frontend: "Local: http://localhost:5173"
✅ Browser: Page loads without errors
✅ Upload: Files upload successfully
✅ AI: Answers appear with supporting chunks
```

**Congratulations! Your Document QA System is ready to use!** 🚀

---

**Last Updated**: When LLM integration was added  
**System Version**: 3.0.0 with Gemini LLM  
**Status**: Production Ready ✅

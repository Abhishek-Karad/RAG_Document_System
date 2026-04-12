# Quick Start Guide

Get the FAISS Document QA system running in 5 minutes!

## 🚀 Start (Option A: Fastest)

This assumes Python 3.9+ and Node.js 16+ are installed.

### 1. Backend
```bash
# Install dependencies
pip install -r requirements.txt

# Start server (will download ~80MB model on first run)
python main.py
```

✅ Backend running at http://localhost:7999

### 2. Frontend
```bash
# In another terminal
cd frontend
npm install
npm run dev
```

✅ Frontend running at http://localhost:5173

**Now open http://localhost:5173 and start uploading documents!**

---

## 🐳 Docker (Option B: One Command)

```bash
docker-compose up
```

Backend: http://localhost:7999  
Frontend: http://localhost:5173

---

## ✅ Verify Installation

```bash
# Check backend health
curl http://localhost:7999/health

# View API docs
open http://localhost:7999/docs
```

---

## 📝 First Steps

1. **Upload a Document**
   - Go to http://localhost:5173
   - Drag & drop a PDF, TXT, or MD file
   - System automatically processes it

2. **Ask a Question**
   - Click "Ask Questions" tab
   - Type: "What is this document about?"
   - See relevant chunks with similarity scores

3. **Adjust Settings**
   - Lower threshold (0.3) for more results
   - Increase top_k to get more chunks
   - Find what works best for your use case

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Make sure port 7999 is free
lsof -i :7999

# Or use different port
PORT=8000 python main.py
```

### Frontend says "Cannot connect to API"
- Check backend is running
- Verify http://localhost:7999/health returns green
- Update .env.local if using different port

### File upload fails
- Max size is 10MB
- Supported formats: .pdf, .txt, .md
- Check disk space

---

## 📚 Next Steps

- Read [README_NEW.md](README_NEW.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Visit http://localhost:7999/docs for API reference

---

**Enjoy building with FAISS!** 🎉

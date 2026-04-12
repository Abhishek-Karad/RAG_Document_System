# FAISS Document QA System

A complete document question-answering system powered by FAISS similarity search, featuring an async FastAPI backend and modern React frontend.

## 🎯 System Architecture

```
├── Backend (FastAPI)
│   ├── Document Upload & Processing
│   ├── PDF/Text Parsing
│   ├── Text Chunking
│   ├── Embedding Generation (SentenceTransformer)
│   └── FAISS Index Management
│
└── Frontend (React + Vite)
    ├── Document Upload Interface
    ├── Document Management
    ├── Question-Answer Interface
    └── Similarity-based Results Display
```

## ✨ Key Features

### Backend
✅ **Multi-format Support**: PDF, TXT, MD files  
✅ **Smart Document Chunking**: Automatic splitting with overlap for context  
✅ **Fast Embeddings**: 384-dimensional vectors via SentenceTransformer  
✅ **FAISS Indexing**: L2-based similarity search  
✅ **Document Management**: Upload, delete, track documents  
✅ **REST API**: Complete endpoints for QA operations  

### Frontend
✅ **Drag & Drop Upload**: Easy file upload interface  
✅ **Document Dashboard**: Manage all uploaded documents  
✅ **Interactive QA**: Ask questions with configurable parameters  
✅ **Smart Results**: Expandable chunks with similarity scores  
✅ **Responsive Design**: Works on desktop and tablets  

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- 2GB+ RAM

### Backend Setup

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Create uploads directory
mkdir -p uploads

# 3. Start backend server
python main.py
```

Backend runs at: **http://localhost:7999**  
API Docs: **http://localhost:7999/docs**

### Frontend Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Start development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

## 📖 Usage Guide

### 1. Upload Documents
1. Go to http://localhost:5173
2. Drag & drop or select a PDF/TXT/MD file
3. System automatically chunks and indexes it

### 2. Ask Questions
1. Click "Ask Questions" tab
2. Type your question
3. Adjust top_k (number of results) and similarity threshold
4. View relevant document chunks

### Example Questions
- "What does this document say about X?"
- "Find all mentions of Y"
- "Summarize the key points"

## 🛠️ API Endpoints

### Documents
```
POST   /upload              - Upload document
GET    /documents           - List all documents
DELETE /documents/{id}      - Delete document
```

### QA
```
POST   /ask                 - Ask a question
GET    /stats               - System statistics
GET    /health              - Health check
```

## 📁 Project Structure

```
FAISS_Backend-main/
├── main.py                 # FastAPI application
├── faiss_manager.py        # FAISS management & embeddings
├── requirements.txt        # Python dependencies
├── uploads/                # Uploaded documents
├── faiss_index.bin        # Persisted FAISS index
├── faiss_metadata.pkl     # Document metadata
└── frontend/               # React application
    ├── src/
    │   ├── App.jsx         # Main component
    │   ├── api.js          # API client
    │   ├── components/
    │   │   ├── DocumentUpload.jsx
    │   │   ├── DocumentList.jsx
    │   │   └── QAInterface.jsx
    │   └── index.css       # Styles
    ├── package.json
    ├── vite.config.js
    └── index.html
```

## 🔧 Configuration

### Backend (main.py)
```python
PORT = 7999                    # Server port
UPLOAD_DIR = "uploads"         # Upload directory
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SIMILARITY_THRESHOLD = 0.50    # Default threshold
```

### Document Chunking (faiss_manager.py)
```python
chunk_size = 500               # Characters per chunk
overlap = 100                  # Overlapping characters
```

## 🎓 Advanced Features

### Custom Embedding Models
```python
# In faiss_manager.py
manager = FAISSIndexManager(model_name="all-mpnet-base-v2")
```

Available models: https://www.sbert.net/docs/pretrained_models.html

### Batch Document Upload
```python
from faiss_manager import FAISSIndexManager

manager = FAISSIndexManager()
manager.load_model()

for doc_file in document_files:
    manager.add_document(doc_file, doc_file.name)

manager.build_index()
manager.save_index()
```

## 📊 Performance

| Operation | Time |
|-----------|------|
| Model Loading | ~2-3s |
| PDF Parsing | ~100-500ms |
| Embedding Generation | ~1-3s |
| Index Building | ~500ms-2s |
| Query Search | ~50-100ms |

## 🐳 Docker Deployment

```bash
# Build image
docker build -t faiss-qa .

# Run container
docker run -p 7999:7999 -v $(pwd)/uploads:/app/uploads faiss-qa
```

## 🌍 Production Deployment

### Environment Variables
```bash
PORT=7999
UPLOAD_DIR=/data/uploads
VITE_API_URL=https://your-api-domain.com
```

### Frontend Build
```bash
cd frontend
npm run build
# Outputs to frontend/dist/
```

## 📋 File Formats

### Supported Input Formats
- **PDF**: .pdf files (text extraction via PyPDF2)
- **Text**: .txt files (plain UTF-8 encoding)
- **Markdown**: .md files (parsed as text)

### File Limits
- Max size: 10MB per file
- Supported encoding: UTF-8

## 🔍 Troubleshooting

### Backend Issues

**Port 7999 Already in Use**
```bash
PORT=8000 python main.py
```

**PDF Processing Fails**
```bash
pip install PyPDF2 --upgrade
```

**Model Download Timeout**
- SentenceTransformer downloads ~80MB on first run
- Check internet connection
- May take 2-5 minutes

### Frontend Issues

**API Connection Error**
- Verify backend running on localhost:7999
- Check CORS settings in main.py
- Update VITE_API_URL in .env.local

**File Upload Fails**
- Check file size (max 10MB)
- Verify file format (.pdf, .txt, .md)
- Check disk space in uploads directory

## 📚 Resources

- [FAISS Documentation](https://faiss.ai/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

## 📝 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a pull request

---

**Built with ❤️ using FastAPI, FAISS, and React** | 2024
    "https://example.com/image2.png"
  ],
  "total_found": 2
}
```

### Information Endpoints

- **GET** `/` - API information
- **GET** `/health` - Server health check  
- **GET** `/stats` - System statistics and index info
- **GET** `/rebuild-index` - Rebuild the FAISS index from current data

## 📁 Project Structure

```
Faiss-backend/
├── images-data.json          # Your image metadata (JSON format)
├── main.py                   # FastAPI web server
├── faiss_manager.py          # FAISS index and search logic
├── integration_client.py     # Python client for easy integration
├── setup.sh                  # Setup and run script
├── requirements.txt          # Python dependencies
├── test_system.py            # Test suite
├── README.md                 # This file
├── faiss_index.bin           # FAISS index (created on first run)
└── venv/                     # Virtual environment (created by setup)
```

## 🔧 Configuration

### Adjust Similarity Threshold

The default similarity threshold is `0.58`. Adjust it based on your needs:

- **Higher threshold** (e.g., 0.7-0.9): More precise, stricter matches
- **Lower threshold** (e.g., 0.3-0.5): More results, broader matches

**In API requests:**
```json
{
  "query": "your search query",
  "similarity_threshold": 0.7
}
```

### Change Embedding Model

Edit `faiss_manager.py` to use a different model:

```python
# Option 1: Current (fastest)
manager = FAISSIndexManager(model_name="all-MiniLM-L6-v2")

# Option 2: Higher quality
manager = FAISSIndexManager(model_name="all-mpnet-base-v2")

# Option 3: Multi-lingual
manager = FAISSIndexManager(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
```

## 📊 How It Works

### 1. **Data Loading**
- Reads your `images-data.json` file
- Extracts text from image metadata (title, description, topic, etc.)

### 2. **Embedding Generation**
- Converts all text into numerical embeddings using sentence transformers
- Creates 384-dimensional vectors that capture semantic meaning
- First time setup downloads the model (~90MB)

### 3. **Index Creation**
- Builds a FAISS L2 index for fast similarity search
- Saves index to `faiss_index.bin` for reuse

### 4. **Search**
- Converts your query text to an embedding
- Finds most similar images using FAISS
- Returns results ranked by similarity score

## 💡 Example Use Cases

### Educational App
```python
# Get images for a lesson topic
images = client.search_images("harmonic frequencies in music")
# Returns images relevant to the topic for classroom use
```

### Content Recommendation
```python
# Suggest related content
query = request.form['user_description']
recommended = client.search_images(query)
# Display recommended images in your UI
```

### Research Tool
```python
# Find similar experimental setups
results = requests.post('http://localhost:7999/search', json={
    "query": "vibration measurement apparatus",
    "top_k": 10
}).json()
# Analyze all matching images
```

## ⚙️ Performance

- **Startup time**: 2-3 seconds (model loading)
- **Index creation**: 1-2 seconds (for ~15 images)
- **Search time**: <10ms per query
- **Memory usage**: ~50MB for 1000 images

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError` or Import errors
**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" on first startup
**Solution:** The server takes 2-3 seconds to load the model. Wait a moment and try again.

### Issue: Slow searches or high memory usage
**Solution:** Consider using `faiss-gpu` instead of `faiss-cpu`:
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

### Issue: No results returned
**Solution:** Check the similarity threshold:
- Try lowering `similarity_threshold` to 0.4 or 0.3
- Check your image metadata in `images-data.json` is complete

### Getting Help
- Check API documentation: http://localhost:7999/docs
- Review console logs for error messages
- Run tests: `python test_system.py`

## 🔄 Integration Examples

### Flask Integration
```python
from flask import Flask
from integration_client import ImageSearchClient

app = Flask(__name__)
search_client = ImageSearchClient()

@app.route('/recommend/<query>')
def recommend(query):
    urls = search_client.search_images(query)
    return {'images': urls}
```

### Direct HTTP Requests
```bash
# Node.js / JavaScript
fetch('http://localhost:7999/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: 'sound waves', top_k: 3})
})
.then(r => r.json())
.then(data => console.log(data))
```

## 📚 API Documentation

After starting the server, visit **http://localhost:7999/docs** for interactive API documentation with live testing.

## 🚀 Next Steps

1. **Customize Your Data**: Update `images-data.json` with your image metadata
2. **Tune Similarity**: Adjust `similarity_threshold` based on your results
3. **Integrate**: Use `integration_client.py` or make direct HTTP calls
4. **Scale**: For large datasets, consider using GPU or IVF indices

## 📝 Data Format

Your `images-data.json` should follow this format:

```json
[
  {
    "id": "sound-1",
    "filename": "sound_wave_diagram.png",
    "url": "https://example.com/images/sound_wave_diagram.png",
    "short_title": "Sound Wave Compression",
    "description": "A diagram showing how sound waves...",
    "topic": "Sound Waves",
    "keywords": ["sound", "waves", "compression"]
  }
]
```

## 📄 License & Credits

Built with:
- **FAISS** - Facebook's vector similarity search library
- **FastAPI** - Modern Python web framework
- **Sentence Transformers** - State-of-the-art sentence embeddings

---

**Ready to search?** 🎯 Start with `./setup.sh run` and visit http://localhost:7999/docs

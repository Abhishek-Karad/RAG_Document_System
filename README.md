# Document Q&A System with RAG & Gemini LLM

A modern document question-answering system that combines vector search (Pinecone) with generative AI (Google Gemini) to give intelligent answers based on your documents.

## What Does It Do?

Upload your documents (PDFs, TXT files), ask questions about them, and get AI-generated answers backed by the actual content from your documents. No more manual searching through files.

**Example:**
- Upload: `Python_Guide.pdf`
- Ask: "What is a list comprehension?"
- Get: Comprehensive answer from the PDF with source references

## How It Works

```
1. Upload Document
   ↓
2. Extract Text & Split into Chunks
   ↓
3. Convert to Vector Embeddings (384D)
   ↓
4. Store in Pinecone (Cloud Vector Database)
   ↓
5. User Asks Question
   ↓
6. Convert Question to Embedding
   ↓
7. Search Pinecone for Similar Chunks (Similarity: 0.65+)
   ↓
8. Send Top Results to Gemini LLM
   ↓
9. Generate AI Answer
   ↓
10. Return to User
```

## Key Features

- **Smart Document Chunking** - Breaks documents at logical boundaries (sentences, paragraphs)
- **Vector Search** - Uses semantic similarity, not keyword matching
- **Cloud Storage** - Pinecone handles scaling, no local disk management
- **LLM Integration** - Google Gemini generates natural, contextual answers
- **Web Interface** - Clean React frontend for easy interaction
- **REST API** - Full API for programmatic access
- **Threshold Control** - Adjust how strict result matching should be

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI (Python) | REST API endpoints |
| **Vector DB** | Pinecone | Semantic search |
| **Embeddings** | Sentence Transformers | Convert text to vectors |
| **LLM** | Google Gemini | Generate answers |
| **Frontend** | React + Vite | Web UI |
| **Deployment** | Docker + Railway | Production hosting |

## Installation

### Prerequisites
- Python 3.13+
- Node.js 18+
- Pinecone account (free tier available)
- Google Generative AI API key

### Backend Setup

```bash
# Clone the repo
git clone <your-repo>
cd FAISS_Backend-main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Get API keys
# 1. Pinecone: https://app.pinecone.io
# 2. Google: https://makersuite.google.com/app/apikey

# Create .env file
cat > .env << EOF
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=document-qa
GEMINI_API_KEY=your_gemini_key
PORT=8000
EOF

# Start the backend
python main.py
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
# Access at http://localhost:5173
```

## Usage

### Via Web Interface

1. **Upload Documents**
   - Go to "Upload Documents" tab
   - Drag & drop or select PDF/TXT files
   - Wait for success message

2. **Ask Questions**
   - Go to "Ask Questions" tab
   - Enter your question
   - AI answer appears with AI Answer box
   - Adjust `top_k` (how many chunks to use) and `threshold` (match strictness) if needed

3. **Manage Documents**
   - View all uploaded documents
   - Delete documents you no longer need

### Via REST API

```bash
# Upload a document
curl -X POST http://localhost:8000/upload \
  -F "file=@myfile.pdf"

# Response:
# {
#   "document_id": "uuid",
#   "document_name": "myfile.pdf",
#   "chunks_created": 25,
#   "message": "Document uploaded successfully..."
# }

# Ask a question with LLM answer
curl -X POST http://localhost:8000/ask-llm \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Python?",
    "top_k": 3,
    "similarity_threshold": 0.65,
    "model": "gemini-2.5-flash"
  }'

# Response:
# {
#   "question": "What is Python?",
#   "answer": "Python is a high-level, interpreted...",
#   "supporting_chunks": [...],
#   "chunk_count": 3,
#   "model": "gemini-2.5-flash"
# }

# Get stats
curl http://localhost:8000/stats

# List documents
curl http://localhost:8000/documents

# Delete a document
curl -X DELETE http://localhost:8000/documents/{document_id}
```

## Configuration

### Similarity Threshold (default: 0.65)

Controls how similar a document chunk must be to the question to be included:

- **0.5** - Loose, catches more (may include irrelevant results)
- **0.65** - Balanced (recommended)
- **0.80** - Strict, only very similar chunks
- **0.95** - Very strict, only exact matches

Lower threshold = more chunks included = longer processing, potentially noisier answers
Higher threshold = fewer chunks = faster, more focused answers

### Top-K (default: 3)

Number of document chunks to retrieve and send to the LLM. More chunks give more context but slower processing.

## API Endpoints

### Documents

```
POST   /upload              - Upload document (PDF/TXT/MD)
GET    /documents           - List all documents
DELETE /documents/{doc_id}  - Delete a document
```

### Search & QA

```
POST /ask                   - Get relevant chunks only (no LLM)
POST /ask-llm              - Get AI-generated answer (with chunks)
```

## Understanding the Architecture

### Chunking Strategy

Documents are split intelligently:
- Respects sentence/paragraph boundaries
- Default chunk size: 400 characters
- Overlap: 50 characters (for context continuity)
- Only chunks > 50 chars are kept

Why? Better semantic meaning. A chunk split mid-sentence loses context.

### Embeddings

Using `all-MiniLM-L6-v2` model (384-dimensional):
- Fast (lightweight)
- High quality for semantic search
- Perfect for production use
- Can process 32 documents in batch

### Pinecone Advantages Over FAISS

| Aspect | FAISS | Pinecone |
|--------|-------|----------|
| **Storage** | Local disk | Cloud |
| **Scaling** | Manual | Automatic |
| **Build Time** | Slow | Real-time indexing |
| **Maintenance** | Self-managed | Managed service |
| **Cost** | Free | Free tier + pay-as-you-go |

## Troubleshooting

### "PINECONE_API_KEY not found"
- Check .env file exists
- Verify key is correct
- Restart backend

### "Gemini API error"
- Verify GEMINI_API_KEY is set
- Check API quota at https://console.cloud.google.com
- Ensure API is enabled in Google Cloud

### "No results found"
- Increase threshold (lower = more results)
- Increase top_k
- Check if document was uploaded successfully

### "Slow responses"
- Reduce top_k
- Increase threshold
- Check Pinecone index stats for performance

### "Document upload fails"
- File size too large? (check Pinecone limits)
- File format supported? (PDF, TXT, MD only)
- Check disk space in uploads/

## Development

### Project Structure

```
.
├── main.py                 # FastAPI app
├── pinecone_manager.py     # Vector DB logic
├── requirements.txt        # Python dependencies
├── Dockerfile              # Production image
├── .env                    # Environment variables
└── frontend/
    ├── package.json
    ├── src/
    │   ├── App.jsx
    │   ├── api.js          # API client
    │   └── components/
    │       ├── QAInterface.jsx
    │       └── DocumentUpload.jsx
    └── vite.config.js
```

### Running Tests

```bash
# Using the API docs
# Visit http://localhost:8000/docs
# Try endpoints interactively

# Or via curl
curl -X POST http://localhost:8000/ask-llm \
  -H "Content-Type: application/json" \
  -d '{"question":"test","top_k":3,"similarity_threshold":0.65}'
```

## Performance Tips

1. **Batch uploads** - Upload multiple small files
2. **Optimize chunks** - Adjust chunking for your document type
3. **Use threshold wisely** - Balance speed vs completeness
4. **Monitor costs** - Check Pinecone usage dashboard

**Project by Abhishek Karad **

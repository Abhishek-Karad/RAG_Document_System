# Frontend Setup Guide

## Overview

The React frontend provides a user-friendly interface for:
- ✅ Uploading documents (PDF, TXT)
- ✅ Viewing indexed documents
- ✅ Asking questions with similarity search
- ✅ Getting AI-formulated answers (Gemini LLM)
- ✅ Viewing supporting document chunks

## Prerequisites

- Node.js (v16+)
- npm or yarn
- Backend running on `http://localhost:7999`

## Installation

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment (Optional)
Create a `.env` file in the `frontend` directory:
```bash
cp .env.example .env
```

Edit `.env`:
```
VITE_API_URL=http://localhost:7999
```

> **Note**: Defaults to `http://localhost:7999` if not specified.

## Development Server

### Start the Frontend
```bash
npm run dev
```

Output:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

Visit: **http://localhost:5173**

## Features

### 1. Document Upload
- **Drag & Drop**: Drag files directly into the upload zone
- **Click to Browse**: Click to select files from your computer
- **Supported Formats**: PDF, TXT, DOC (via backend)
- **Validation**: File size and type checked before upload
- **Feedback**: Success/error messages displayed

### 2. Document Management
- **List View**: See all uploaded documents with metadata
  - Document name
  - Number of chunks created
  - Upload date
- **Delete**: Remove documents from the index
- **Auto Refresh**: List updates after uploads/deletes

### 3. Question & Answer (with AI)
- **Input**: Enter your question about documents
- **Toggle**: "Use AI to formulate answer" checkbox
  - ✅ **ON**: Calls `/ask-llm` endpoint → AI answer + supporting chunks
  - ❌ **OFF**: Calls `/ask` endpoint → raw chunks only
- **Top-K**: Number of document chunks to retrieve (1-10)
- **Threshold**: Similarity score filter (0.0-1.0)

### 4. Results Display

#### When AI is ON:
```
┌─────────────────────────────────────┐
│ 🌟 AI Answer                        │
│                                     │
│ [Comprehensive AI-generated         │
│  answer using Gemini]               │
└─────────────────────────────────────┘

3 Supporting Document Chunks:

┌─────────────────────────────────────┐
│ #1 document.pdf - Chunk 5           │
│ Relevance: 87% [↓ Expand]           │
└─────────────────────────────────────┘
...
```

#### When AI is OFF:
```
Found 3 relevant chunks for your question

┌─────────────────────────────────────┐
│ #1 document.pdf - Chunk 5           │
│ Similarity: 87% [↓ Expand]          │
│                                     │
│ [Click to expand and view chunk text]
└─────────────────────────────────────┘
...
```

## Component Structure

### App.jsx
- Main container
- State management (documents, results)
- Routes between Upload, List, QA views

### Components

#### DocumentUpload.jsx
```
┌─────────────────────────────────┐
│  Drop files or click to upload   │
│                                 │
│  Supported: PDF, TXT, DOC       │
│  Max size: 50MB                 │
└─────────────────────────────────┘
[Progress...] [Cancel]
```

#### DocumentList.jsx
```
┌─────────────────────────────────┐
│ Your Documents                  │
│                                 │
│ 📄 file1.pdf (125 chunks)   [×] │
│ 📄 file2.txt (89 chunks)    [×] │
│ 📄 file3.pdf (201 chunks)   [×] │
└─────────────────────────────────┘
```

#### QAInterface.jsx
```
┌──────────────────────────────────┐
│ Ask a Question                   │
│                                  │
│ [Enter your question...] [Send]  │
│                                  │
│ Top-K: [3] | Threshold: [0.50]  │
│ ☑ Use AI to formulate answer    │
└──────────────────────────────────┘
```

#### SearchResults.jsx
- Dynamic rendering based on response type
- Expandable chunks
- Similarity/relevance scoring

## Usage Workflow

### 1. Upload Documents
1. Click on "Upload Documents" tab
2. Drag & drop or click to select files
3. Wait for success message
4. Documents appear in "Your Documents" list

### 2. Ask a Question
1. Click on "Ask Questions" tab
2. Enter your question
3. (Optional) Adjust top_k and threshold
4. **Enable "Use AI to formulate answer"** for LLM-powered results
5. Click send button or press Enter

### 3. View AI Answer
1. AI Answer appears in prominent blue box at top
2. Supporting chunks listed below with relevance scores
3. Click chunks to expand and read full text

### 4. Manage Documents
1. Click on "Your Documents" tab
2. Click [×] button on any document to delete
3. Document is permanently removed from index

## Styling

### Built with:
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide React**: Beautiful SVG icons
- **Custom CSS**: `index.css` for animations

### Key Classes
- `bg-gradient-to-r`: Gradient backgrounds
- `rounded-lg`: Rounded corners
- `shadow-md`: Subtle shadows
- `hover:`: Interactive states
- `disabled:`: Disabled states

### Color Scheme
- **Primary**: Blue (#3B82F6)
- **Secondary**: Indigo (#6366F1)
- **Accent**: Gradient (Blue → Indigo)
- **Neutral**: Gray scale (50-900)

## API Integration

### Base URL
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:7999';
```

### Methods (api.js)

#### Upload Document
```javascript
apiClient.uploadDocument(file)
// Returns: { document_id, filename, num_chunks, ... }
```

#### Get Documents
```javascript
apiClient.getDocuments()
// Returns: [ { id, name, chunks, ... }, ... ]
```

#### Delete Document
```javascript
apiClient.deleteDocument(documentId)
// Returns: { status: "deleted" }
```

#### Ask Question (Chunks Only)
```javascript
apiClient.askQuestion(question, topK, threshold)
// Returns: { results: [...], total_results: 3 }
```

#### Ask with LLM (NEW)
```javascript
apiClient.askQuestionWithLLM(question, topK, threshold, model)
// Returns: { answer, supporting_chunks, chunk_count, ... }
```

## Troubleshooting

### "Cannot reach backend"
**Error**: Connection refused on `http://localhost:7999`

**Solution**:
```bash
# Start backend in another terminal
cd ..  # Go back to root
python main.py

# Or with docker
docker-compose up
```

### "AI Answer not working"
**Error**: "Gemini API not configured" in UI

**Solution**:
```bash
# Backend needs GEMINI_API_KEY environment variable
export GEMINI_API_KEY=your_key_here
python main.py
```

### "Uploads failing"
**Error**: Cannot upload files

**Solution**:
1. Check backend is running
2. Try smaller file
3. Check CORS headers in backend logs
4. Ensure `uploads/` directory exists on backend

### "Slow performance"
**Optimize**:
- Reduce `top_k` value (fewer chunks to process)
- Increase `threshold` (filter lower-relevance chunks)
- Disable AI mode temporarily (faster chunk retrieval)

## Production Build

### Build for Deployment
```bash
npm run build
```

Creates `dist/` directory with optimized files.

### Serve Production Build
```bash
npm run preview
```

### Docker Deployment
See `Dockerfile` in frontend directory:
```bash
docker build -t faiss-frontend .
docker run -p 5173:5173 faiss-frontend
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:7999` | Backend API URL |
| `VITE_API_TIMEOUT` | `30000` | Request timeout (ms) |

## Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Check code quality (if configured)
```

## Browser Support

- Chrome/Edge (Latest)
- Firefox (Latest)
- Safari (Latest)
- Mobile browsers with JavaScript enabled

## Performance Tips

1. **Batch Uploads**: Upload multiple documents at once
2. **Smart Parameters**: 
   - Lower `top_k` for faster results
   - Higher `threshold` to filter noise
3. **Clear Cache**: Browser DevTools → Application → Clear Storage
4. **Monitor**: Open DevTools → Network tab to see requests

## Development

### Hot Module Reloading (HMR)
Changes to components automatically reload in browser without full refresh.

### Debug Mode
```javascript
// In api.js, add logging
api.interceptors.response.use(
  response => console.log('Response:', response),
  error => console.error('Error:', error)
);
```

### React DevTools
Install Chrome extension: "React Developer Tools" for inspecting components

## Security Notes

- 🔒 **CORS**: Configure backend CORS settings for production
- 🔐 **API Key**: Never commit `.env` file with real keys
- 🛡️ **Validation**: All inputs validated on frontend & backend
- 🔄 **HTTPS**: Use HTTPS in production

## Support

For issues:
1. Check the main `README_NEW.md`
2. Review `LLM_INTEGRATION.md` for AI-specific settings
3. Check backend logs: `python main.py` output
4. Verify all prerequisites installed

---

**Ready to ask questions?** 🚀

1. Start backend: `python main.py`
2. Start frontend: `npm run dev`
3. Visit `http://localhost:5173`
4. Upload a document
5. Ask questions (with AI enabled!)

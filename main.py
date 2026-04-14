from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
import shutil
from dotenv import load_dotenv
from pinecone_manager import PineconeIndexManager, initialize_pinecone_system
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pinecone Document QA API with LLM",
    description="API for uploading documents and asking questions using Pinecone + Gemini LLM",
    version="3.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8999", 
        "http://localhost:5173",
        
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------

# Global Pinecone manager instance
faiss_manager: Optional[PineconeIndexManager] = None

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Get Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", None)


# ===================== DATA MODELS =====================

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3
    similarity_threshold: float = 0.65


class LLMQuestionRequest(BaseModel):
    question: str
    top_k: int = 3
    similarity_threshold: float = 0.65
    model: str = "gemini-2.5-flash"  # Gemini model to use (gemini-pro is deprecated)


class ChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    chunk_index: int
    text: str
    similarity_score: float
    rank: int


class QAResponse(BaseModel):
    question: str
    results: List[ChunkResult]
    total_results: int
    message: Optional[str] = None


class LLMAnswerResponse(BaseModel):
    question: str
    answer: str  # Formulated answer from LLM
    supporting_chunks: List[ChunkResult]
    chunk_count: int
    model: str  # LLM model used


class DocumentInfo(BaseModel):
    document_id: str
    name: str
    chunk_count: int
    total_characters: int


class DocumentsResponse(BaseModel):
    documents: List[DocumentInfo]
    total_documents: int


class UploadResponse(BaseModel):
    document_id: str
    document_name: str
    chunks_created: int
    message: str


# ===================== STARTUP EVENT =====================

@app.on_event("startup")
async def startup_event():
    global faiss_manager
    
    try:
        logger.info("Initializing Pinecone system for documents...")
        
        faiss_manager = initialize_pinecone_system()
        
        logger.info("Pinecone system initialized successfully")
        
        # Configure Gemini API if key is available
        if GEMINI_API_KEY:
            try:
                # Gemini configuration is handled directly in pinecone_manager
                # Just verify the API key is set
                logger.info("Gemini LLM will be used for answer generation")
            except Exception as e:
                logger.warning(f"Could not configure Gemini LLM: {e}. LLM features will be unavailable.")
        else:
            logger.warning("GEMINI_API_KEY not set. LLM features will be unavailable. Set via environment variable.")
    
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone system: {e}")
        raise


# ===================== API ENDPOINTS =====================

@app.get("/")
async def root():
    embedding_info = ""
    if faiss_manager and faiss_manager.embedding_dimension:
        embedding_info = f" | {faiss_manager.embedding_dimension}D embeddings"
    
    return {
        "message": "Pinecone Document QA API with LLM",
        "version": "3.0.0",
        "model": f"{faiss_manager.model_name if faiss_manager else 'loading'}{embedding_info}",
        "endpoints": {
            "upload": "POST /upload",
            "ask": "POST /ask (chunks only)",
            "ask_with_llm": "POST /ask-llm (formatted answer)",
            "documents": "GET /documents",
            "delete_document": "DELETE /documents/{document_id}",
            "stats": "GET /stats"
        }
    }


@app.get("/stats")
async def get_stats():
    global faiss_manager
    
    if faiss_manager is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready")
    
    return {
        "total_documents": len(faiss_manager.document_metadata),
        "total_chunks": sum(doc['chunk_count'] for doc in faiss_manager.document_metadata.values()),
        "model_name": faiss_manager.model_name,
        "embedding_dimension": faiss_manager.embedding_dimension,
        "system_status": "ready",
        "vector_store": "Pinecone"
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF or text file) and add it to the Pinecone index.
    """
    global faiss_manager
    
    if faiss_manager is None or faiss_manager.model is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready")
    
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.txt', '.md'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # Add document to Pinecone
        doc_result = faiss_manager.add_document(file_path, file.filename)
        
        # No need to rebuild index - Pinecone handles indexing automatically
        
        logger.info(f"Document processed and uploaded to Pinecone")
        
        return UploadResponse(
            document_id=doc_result['document_id'],
            document_name=doc_result['document_name'],
            chunks_created=doc_result['chunks_created'],
            message=f"Document '{file.filename}' uploaded successfully with {doc_result['chunks_created']} chunks"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/documents", response_model=DocumentsResponse)
async def get_documents():
    """
    Get list of all uploaded documents.
    """
    global faiss_manager
    
    if faiss_manager is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready")
    
    documents = faiss_manager.get_documents()
    documents_info = [
        DocumentInfo(
            document_id=doc['document_id'],
            name=doc['name'],
            chunk_count=doc['chunk_count'],
            total_characters=doc['total_characters']
        )
        for doc in documents
    ]
    
    return DocumentsResponse(
        documents=documents_info,
        total_documents=len(documents_info)
    )


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the Pinecone index.
    """
    global faiss_manager
    
    if faiss_manager is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready")
    
    try:
        if document_id not in faiss_manager.document_metadata:
            raise HTTPException(status_code=404, detail="Document not found")
        
        faiss_manager.delete_document(document_id)
        
        return {"message": f"Document {document_id} deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.post("/ask", response_model=QAResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get relevant document chunks based on similarity.
    """
    global faiss_manager
    
    if faiss_manager is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready. Please upload documents first.")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if request.top_k <= 0 or request.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
    
    try:
        raw_results = faiss_manager.search(
            request.question,
            request.top_k,
            request.similarity_threshold
        )
        
        results = [
            ChunkResult(
                chunk_id=r['chunk_id'],
                document_id=r['document_id'],
                document_name=r['document_name'],
                chunk_index=r['chunk_index'],
                text=r['text'],
                similarity_score=r['similarity_score'],
                rank=r['rank']
            )
            for r in raw_results
        ]
        
        message = None
        if len(results) == 0:
            message = f"No relevant chunks found above similarity threshold {request.similarity_threshold}"
            logger.info(f"No results for question: '{request.question}'")
        
        return QAResponse(
            question=request.question,
            results=results,
            total_results=len(results),
            message=message
        )
    
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")


@app.post("/ask-llm", response_model=LLMAnswerResponse)
async def ask_with_llm(request: LLMQuestionRequest):
    """
    Ask a question and get a formatted answer generated by Gemini LLM based on relevant document chunks.
    """
    global faiss_manager
    
    if faiss_manager is None:
        raise HTTPException(status_code=503, detail="Pinecone system not ready. Please upload documents first.")
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="Gemini API key not configured. Set GEMINI_API_KEY environment variable.")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if request.top_k <= 0 or request.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")
    
    try:
        # Use the complete QA pipeline with LLM
        qa_result = faiss_manager.answer_question(
            request.question,
            request.top_k,
            request.similarity_threshold,
            request.model
        )
        
        # Convert chunks to ChunkResult objects
        supporting_chunks = [
            ChunkResult(
                chunk_id=chunk['chunk_id'],
                document_id=chunk['document_id'],
                document_name=chunk['document_name'],
                chunk_index=chunk['chunk_index'],
                text=chunk['text'],
                similarity_score=chunk['similarity_score'],
                rank=chunk['rank']
            )
            for chunk in qa_result['supporting_chunks']
        ]
        
        logger.info(f"Generated LLM answer for question: '{request.question}'")
        
        return LLMAnswerResponse(
            question=request.question,
            answer=qa_result['answer'],
            supporting_chunks=supporting_chunks,
            chunk_count=qa_result['chunk_count'],
            model=qa_result['model']
        )
    
    except Exception as e:
        logger.error(f"LLM question answering failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM QA failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 7999))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
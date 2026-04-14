import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import os
import uuid
import pickle
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PDF imports
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

# LLM imports
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """
    Manages FAISS index creation and similarity search for document chunks.
    Uses high-dimensional embeddings (768D) and intelligent semantic chunking.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the FAISS index manager for documents.
        
        Args:
            model_name: Name of the sentence transformer model to use for embeddings
                       Default: all-MiniLM-L12-v2 (384-dimensional, fast & high quality)
                       Alternative: all-mpnet-base-v2 (768-dimensional, slower startup)
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunks = []  # Store chunk metadata and content
        self.embeddings = None
        self.document_metadata = {}  # Store document info
        self.embedding_dimension = None  # Will be set after model load
        
    def load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Determine embedding dimension
            test_embedding = self.model.encode(["test"])
            self.embedding_dimension = test_embedding.shape[1]
            
            logger.info(f"Model loaded successfully - Embedding dimension: {self.embedding_dimension}D")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from PDF
        """
        if PdfReader is None:
            raise ImportError("pypdf is required for PDF processing. Install it with: pip install pypdf")
        
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            logger.info(f"Extracted {len(text)} characters from {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """
        Split text into semantically meaningful overlapping chunks.
        Respects paragraph/sentence boundaries for better context preservation.
        
        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk in characters (default: 800)
            overlap: Number of overlapping characters between chunks (default: 200)
            
        Returns:
            List of text chunks
        """
        # Clean text: normalize whitespace, handle special characters
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = ' '.join(text.split())  # Normalize spaces
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Define the target end position
            end_pos = min(current_pos + chunk_size, len(text))
            
            # If at end of text, just take remaining
            if end_pos == len(text):
                chunk = text[current_pos:end_pos].strip()
                if chunk and len(chunk) > 50:  # Only add if substantial (50+ chars)
                    chunks.append(chunk)
                break
            
            # Try to find a sentence boundary (period, exclamation, question mark)
            search_end = min(end_pos, current_pos + chunk_size + 100)
            best_break = end_pos
            
            # Look backwards from target end for sentence boundary
            for break_char in ['.', '!', '?', '\n']:
                last_break = text.rfind(break_char, current_pos + 100, search_end)
                if last_break > current_pos + 100:
                    best_break = last_break + 1
                    break
            
            # If no sentence boundary, try to break at word boundary
            if best_break == end_pos:
                space_pos = text.rfind(' ', current_pos + 100, end_pos)
                if space_pos > current_pos + 100:
                    best_break = space_pos + 1
            
            chunk = text[current_pos:best_break].strip()
            
            if chunk and len(chunk) > 50:  # Only add substantial chunks
                chunks.append(chunk)
                # Move forward with overlap for context continuity
                current_pos = best_break - overlap
            else:
                # If we couldn't create a good chunk, skip ahead
                current_pos = best_break
        
        logger.info(f"Created {len(chunks)} semantic chunks (avg length: {sum(len(c) for c in chunks)//max(len(chunks), 1)} chars)")
        return chunks
    
    def add_document(self, file_path: str, document_name: str) -> Dict[str, Any]:
        """
        Add a document (PDF or text) to the index.
        
        Args:
            file_path: Path to the uploaded file
            document_name: Name of the document
            
        Returns:
            Dictionary with document metadata
        """
        try:
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            else:
                # Assume text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Chunk the text
            text_chunks = self.chunk_text(text)
            
            # Store chunks with metadata
            for chunk_idx, chunk in enumerate(text_chunks):
                chunk_record = {
                    'chunk_id': f"{doc_id}_chunk_{chunk_idx}",
                    'document_id': doc_id,
                    'document_name': document_name,
                    'chunk_index': chunk_idx,
                    'text': chunk
                }
                self.chunks.append(chunk_record)
            
            # Store document metadata
            self.document_metadata[doc_id] = {
                'name': document_name,
                'file_path': file_path,
                'chunk_count': len(text_chunks),
                'total_characters': len(text),
                'uploaded_at': str(__import__('datetime').datetime.now())
            }
            
            logger.info(f"Added document '{document_name}' with {len(text_chunks)} chunks")
            return {
                'document_id': doc_id,
                'document_name': document_name,
                'chunks_created': len(text_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def build_index(self):
        """Build FAISS index from document chunks."""
        if not self.model:
            self.load_model()
        
        if not self.chunks:
            raise ValueError("No chunks loaded. Add documents first using add_document().")
        
        logger.info("Creating embeddings for all chunks...")
        
        # Extract chunk texts
        texts = [chunk['text'] for chunk in self.chunks]
        
        # Generate embeddings
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            emb = self.model.encode(batch, show_progress_bar=True)
            all_embeddings.append(emb)

        self.embeddings = np.vstack(all_embeddings)
        logger.info(f"Created embeddings with shape: {self.embeddings.shape}")
        
        # Build FAISS index
        logger.info("Building FAISS index...")
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings.astype('float32'))
        
        logger.info(f"FAISS index built successfully with {self.index.ntotal} vectors")
    
    def save_index(self, index_path: str = "faiss_index.bin", metadata_path: str = "faiss_metadata.pkl"):
        """
        Save the FAISS index and metadata to disk.
        
        Args:
            index_path: Path where to save the index
            metadata_path: Path where to save metadata
        """
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
        
        faiss.write_index(self.index, index_path)
        
        # Save chunks and metadata
        metadata = {
            'chunks': self.chunks,
            'document_metadata': self.document_metadata,
            'model_name': self.model_name
        }
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Index saved to {index_path} and metadata to {metadata_path}")
    
    def load_index(self, index_path: str = "faiss_index.bin", metadata_path: str = "faiss_metadata.pkl"):
        """
        Load FAISS index and metadata from disk.
        
        Args:
            index_path: Path to the saved index
            metadata_path: Path to the saved metadata
        """
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Index or metadata file not found")
        
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.chunks = metadata['chunks']
        self.document_metadata = metadata['document_metadata']
        
        logger.info(f"Index loaded from {index_path} with {len(self.chunks)} chunks")
    
    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.50) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks based on query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return (default: 3)
            similarity_threshold: Minimum similarity score to include results (0.0 to 1.0)
            
        Returns:
            List of dictionaries containing relevant chunks
        """
        if not self.model:
            self.load_model()
        
        if self.index is None:
            raise ValueError("No index available. Build or load index first.")
        
        if not self.chunks:
            raise ValueError("No chunks available.")
        
        # Create embedding for query
        query_embedding = self.model.encode([query])
        
        # Search in FAISS index
        search_k = min(top_k * 5, len(self.chunks))
        distances, indices = self.index.search(query_embedding.astype('float32'), search_k)
        
        logger.info(f"\nQuery: '{query}' | Threshold: {similarity_threshold} | Top K: {top_k}")
        
        # Prepare results with similarity filtering
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                # Convert distance to similarity score
                similarity_score = float(1.0 / (1.0 + distance))
                
                if similarity_score >= similarity_threshold:
                    chunk = self.chunks[idx].copy()
                    chunk['similarity_score'] = similarity_score
                    chunk['rank'] = len(results) + 1
                    results.append(chunk)
                    
                    logger.info(f"  ✓ #{len(results)}: {chunk['document_name']} | Score: {similarity_score:.4f}")
                    
                    if len(results) >= top_k:
                        break
        
        logger.info(f"Retrieved {len(results)} relevant chunks\n")
        return results
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get all uploaded documents metadata."""
        documents = []
        for doc_id, metadata in self.document_metadata.items():
            doc_info = metadata.copy()
            doc_info['document_id'] = doc_id
            documents.append(doc_info)
        return documents
    
    def delete_document(self, document_id: str):
        """Delete a document and its chunks from the index."""
        # Remove chunks belonging to this document
        self.chunks = [c for c in self.chunks if c['document_id'] != document_id]
        
        # Remove document metadata
        if document_id in self.document_metadata:
            del self.document_metadata[document_id]
        
        # Rebuild index without deleted chunks
        if self.chunks:
            self.build_index()
        else:
            self.index = None
            self.embeddings = None
        
        logger.info(f"Deleted document {document_id} and rebuilt index")
    
    def configure_llm(self, api_key: str):
        """
        Configure Google Generative AI (Gemini) with API key.
        
        Args:
            api_key: Google Generative AI API key
        """
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")
        
        try:
            genai.configure(api_key=api_key)
            logger.info("Gemini API configured successfully")
        except Exception as e:
            logger.error(f"Error configuring Gemini API: {e}")
            raise
    
    def generate_answer(self, query: str, chunks: List[Dict[str, Any]], model_name: str = "gemini-2.5-flash") -> str:
        """
        Generate a comprehensive answer using Gemini LLM based on retrieved chunks.
        
        Args:
            query: User's question
            chunks: List of relevant document chunks from search
            model_name: Gemini model to use (default: gemini-2.5-flash)
            
        Returns:
            Formulated answer from the LLM
        """
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")
        
        if not chunks:
            return "No relevant information found in the documents to answer your question."
        
        try:
            # Build context from chunks
            context = "\n\n".join([
                f"Source: {chunk['document_name']} (Chunk {chunk['chunk_index']})\n"
                f"Relevance: {chunk.get('similarity_score', 0):.2%}\n"
                f"Content:\n{chunk['text']}"
                for chunk in chunks
            ])
            
            # Create prompt for LLM
            prompt = f"""Based on the following document excerpts, please answer the user's question comprehensively and accurately.

Document Excerpts:
{context}

User Question: {query}

Please provide a clear, well-structured answer that:
1. Directly addresses the question
2. References the relevant information from the documents
3. Is concise but complete
4. Indicates if information is not available in the documents"""
            
            logger.info(f"Generating answer using Gemini for query: '{query}'")
            
            # Initialize model and generate response
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            
            answer = response.text
            logger.info(f"Generated answer successfully ({len(answer)} characters)")
            
            return answer
        
        except Exception as e:
            logger.error(f"Error generating answer with Gemini: {e}")
            raise
    
    def answer_question(self, query: str, top_k: int = 3, similarity_threshold: float = 0.50, 
                       model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
        """
        Complete QA pipeline: search for relevant chunks and generate an LLM answer.
        
        Args:
            query: User's question
            top_k: Number of relevant chunks to retrieve
            similarity_threshold: Minimum similarity score for chunks
            model_name: Gemini model to use
            
        Returns:
            Dictionary with chunks, generated answer, and metadata
        """
        # Step 1: Search for relevant chunks
        chunks = self.search(query, top_k, similarity_threshold)
        
        # Step 2: Generate answer using LLM
        answer = self.generate_answer(query, chunks, model_name)
        
        return {
            'query': query,
            'answer': answer,
            'supporting_chunks': chunks,
            'chunk_count': len(chunks),
            'model': model_name
        }


def initialize_faiss_system() -> FAISSIndexManager:
    """
    Initialize an empty FAISS system for document uploads.
    
    Returns:
        Initialized FAISSIndexManager instance
    """
    manager = FAISSIndexManager()
    manager.load_model()
    return manager
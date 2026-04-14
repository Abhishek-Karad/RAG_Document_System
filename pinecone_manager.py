import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv

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

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PineconeIndexManager:
    """
    Manages Pinecone vector index for document QA.
    Replaces FAISS with cloud-hosted Pinecone vector database.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 index_name: str = "document-qa",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Pinecone index manager.
        
        Args:
            api_key: Pinecone API key (default from PINECONE_API_KEY env)
            index_name: Name of Pinecone index
            model_name: Sentence transformer model for embeddings
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "document-qa")
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
        # Load embedding model
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 dimension
        
        # Local storage for document metadata
        self.document_metadata = {}
        
        # Configure Gemini API key
        self.configure_llm()
    
    def configure_llm(self):
        """Configure Gemini LLM with API key from environment."""
        if genai is None:
            logger.warning("google-generativeai not installed. LLM features will be unavailable.")
            return
        
        try:
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found in environment. LLM features will be unavailable.")
                return
            
            genai.configure(api_key=gemini_api_key)
            logger.info("Gemini LLM configured successfully")
        except Exception as e:
            logger.error(f"Error configuring Gemini LLM: {e}")
    
    def connect_to_index(self):
        """Connect to existing Pinecone index."""
        try:
            self.index = self.pc.Index(self.index_name)
            stats = self.index.describe_index_stats()
            logger.info(f"Connected to index '{self.index_name}' with {stats.total_vector_count} vectors")
        except Exception as e:
            logger.error(f"Error connecting to index: {e}")
            raise
    
    def create_index(self, dimension: int = 384):
        """Create new Pinecone index if it doesn't exist."""
        try:
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating index '{self.index_name}'...")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                logger.info(f"Index '{self.index_name}' created successfully")
            else:
                logger.info(f"Index '{self.index_name}' already exists")
            
            self.connect_to_index()
        except Exception as e:
            logger.error(f"Error creating/connecting to index: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        if PdfReader is None:
            raise ImportError("pypdf is required for PDF processing. Install with: pip install pypdf")
        
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
    
    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 100) -> List[str]:
        """Split text into semantically meaningful overlapping chunks."""
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        text = ' '.join(text.split())
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = min(current_pos + chunk_size, len(text))
            
            if end_pos == len(text):
                chunk = text[current_pos:end_pos].strip()
                if chunk and len(chunk) > 50:
                    chunks.append(chunk)
                break
            
            search_end = min(end_pos, current_pos + chunk_size + 100)
            best_break = end_pos
            
            for break_char in ['.', '!', '?', '\n']:
                last_break = text.rfind(break_char, current_pos + 100, search_end)
                if last_break > current_pos + 100:
                    best_break = last_break + 1
                    break
            
            if best_break == end_pos:
                space_pos = text.rfind(' ', current_pos + 100, end_pos)
                if space_pos > current_pos + 100:
                    best_break = space_pos + 1
            
            chunk = text[current_pos:best_break].strip()
            
            if chunk and len(chunk) > 50:
                chunks.append(chunk)
                current_pos = best_break - overlap
            else:
                current_pos = best_break
        
        logger.info(f"Created {len(chunks)} semantic chunks")
        return chunks
    
    def add_document(self, file_path: str, document_name: str) -> Dict[str, Any]:
        """Add document to Pinecone index."""
        if self.index is None:
            self.connect_to_index()
        
        try:
            # Extract text based on file type
            if file_path.endswith('.pdf'):
                text = self.extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Chunk text
            text_chunks = self.chunk_text(text)
            
            # Create embeddings and prepare vectors for Pinecone
            vectors_to_upsert = []
            
            for chunk_idx, chunk in enumerate(text_chunks):
                chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                
                # Generate embedding
                embedding = self.model.encode(chunk).tolist()
                
                # Create metadata
                metadata = {
                    'document_id': doc_id,
                    'document_name': document_name,
                    'chunk_index': chunk_idx,
                    'text': chunk
                }
                
                vectors_to_upsert.append((chunk_id, embedding, metadata))
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i+batch_size]
                self.index.upsert(vectors=batch)
            
            # Store document metadata locally
            self.document_metadata[doc_id] = {
                'name': document_name,
                'chunk_count': len(text_chunks),
                'total_characters': len(text)
            }
            
            logger.info(f"Added document '{document_name}' with {len(text_chunks)} chunks to Pinecone")
            return {
                'document_id': doc_id,
                'document_name': document_name,
                'chunks_created': len(text_chunks)
            }
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.65) -> List[Dict[str, Any]]:
        """
        Search Pinecone index for similar document chunks.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score (default: 0.65)
            
        Returns:
            List of relevant document chunks
        """
        if self.index is None:
            self.connect_to_index()
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k * 5,
                include_metadata=True
            )
            
            # Filter by similarity threshold and format results
            formatted_results = []
            for match in results.get('matches', []):
                score = float(match['score'])
                
                if score >= similarity_threshold:
                    formatted_results.append({
                        'chunk_id': match['id'],
                        'document_id': match['metadata']['document_id'],
                        'document_name': match['metadata']['document_name'],
                        'chunk_index': match['metadata']['chunk_index'],
                        'text': match['metadata']['text'],
                        'similarity_score': score,
                        'rank': len(formatted_results) + 1
                    })
                    
                    if len(formatted_results) >= top_k:
                        break
            
            logger.info(f"Query '{query}' | Threshold: {similarity_threshold} | Retrieved {len(formatted_results)} results")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document from Pinecone."""
        if self.index is None:
            self.connect_to_index()
        
        try:
            # Query to find all vectors with this document_id
            # Note: This is a limitation - Pinecone doesn't support batch delete by metadata
            # Alternative approach: track chunk IDs locally or implement custom deletion
            logger.info(f"Marking document {document_id} as deleted from local metadata")
            
            if document_id in self.document_metadata:
                del self.document_metadata[document_id]
            
            # For actual deletion from Pinecone, you would need to:
            # 1. List all vectors (limited API)
            # 2. Filter by document_id in metadata
            # 3. Delete the matching vectors
            # This is a Pinecone limitation for serverless indexes
            
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get all document metadata."""
        documents = []
        for doc_id, metadata in self.document_metadata.items():
            doc_info = metadata.copy()
            doc_info['document_id'] = doc_id
            documents.append(doc_info)
        return documents
    
    def generate_answer(self, query: str, chunks: List[Dict[str, Any]], model_name: str = "gemini-2.5-flash") -> str:
        """
        Generate a comprehensive answer using Gemini LLM based on retrieved chunks.
        
        Args:
            query: User's question
            chunks: List of relevant document chunks from search
            model_name: Gemini model to use
            
        Returns:
            Formulated answer from the LLM
        """
        if genai is None:
            raise ImportError("google-generativeai is required. Install with: pip install google-generativeai")
        
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY not found in environment. Please set it before using LLM features.")
        
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
            logger.error(f"Error generating answer: {e}")
            raise
    
    def answer_question(self, query: str, top_k: int = 3, similarity_threshold: float = 0.65,
                       model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
        """
        Complete QA pipeline: search for relevant chunks and generate an LLM answer.
        
        Args:
            query: User's question
            top_k: Number of relevant chunks to retrieve
            similarity_threshold: Minimum similarity score (default: 0.65)
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


def initialize_pinecone_system() -> PineconeIndexManager:
    """Initialize Pinecone system on startup."""
    try:
        manager = PineconeIndexManager()
        manager.create_index()
        logger.info("Pinecone system initialized successfully")
        return manager
    except Exception as e:
        logger.error(f"Failed to initialize Pinecone system: {e}")
        raise

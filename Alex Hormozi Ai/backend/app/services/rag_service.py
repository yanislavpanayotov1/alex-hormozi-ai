"""
RAG (Retrieval-Augmented Generation) Service for Hormozi AI

This service handles the core RAG functionality including:
- Vector database queries
- Context retrieval
- Response generation using OpenAI
- Source citation management
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import openai
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class RAGService:
    """Main service for RAG operations"""
    
    def __init__(self, 
                 chroma_path: str = "./data/chroma",
                 collection_name: str = "hormozi_knowledge",
                 openai_api_key: Optional[str] = None,
                 model: str = "gpt-4",
                 temperature: float = 0.7):
        
        self.chroma_path = Path(chroma_path)
        self.collection_name = collection_name
        self.model = model
        self.temperature = temperature
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize ChromaDB
        self._init_chroma_db()
        
    def _init_chroma_db(self):
        """Initialize ChromaDB client and collection"""
        try:
            if not self.chroma_path.exists():
                logger.warning(f"ChromaDB path does not exist: {self.chroma_path}")
                logger.info("Knowledge base not found. Please run the training pipeline first.")
                self.chroma_client = None
                self.collection = None
                return
                
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.chroma_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=False
                )
            )
            
            # Get the collection
            try:
                self.collection = self.chroma_client.get_collection(self.collection_name)
                collection_count = self.collection.count()
                logger.info(f"Connected to ChromaDB collection '{self.collection_name}' with {collection_count} documents")
            except Exception as e:
                logger.warning(f"Collection '{self.collection_name}' not found: {e}")
                self.collection = None
                
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None
    
    def is_knowledge_base_available(self) -> bool:
        """Check if the knowledge base is available"""
        return self.collection is not None and self.collection.count() > 0
    
    def search_knowledge_base(self, 
                            query: str, 
                            n_results: int = 5,
                            min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant context"""
        
        if not self.is_knowledge_base_available():
            logger.warning("Knowledge base not available")
            return []
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results['documents'] or not results['documents'][0]:
                logger.info(f"No results found for query: {query}")
                return []
            
            # Process results
            processed_results = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
            distances = results['distances'][0] if results['distances'] else [0] * len(documents)
            
            for doc, metadata, distance in zip(documents, metadatas, distances):
                # Convert distance to similarity (ChromaDB uses cosine distance)
                similarity = 1 - distance
                
                if similarity >= min_similarity:
                    processed_results.append({
                        'content': doc,
                        'metadata': metadata,
                        'similarity': similarity,
                        'book': metadata.get('book_title', 'Unknown'),
                        'chapter': metadata.get('chapter', 'Unknown'),
                        'page_number': metadata.get('page_number', 0)
                    })
            
            logger.info(f"Found {len(processed_results)} relevant results for query")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def generate_response(self, 
                         query: str, 
                         context_results: List[Dict[str, Any]],
                         conversation_history: Optional[List[Dict[str, str]]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        """Generate a response using RAG"""
        
        # Prepare context from search results
        context_text = self._prepare_context(context_results)
        
        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(query, context_text)
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Keep last 6 messages for context
        
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # Generate response using OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000
            )
            
            generated_text = response.choices[0].message.content
            
            # Prepare sources for citation
            sources = self._prepare_sources(context_results)
            
            logger.info(f"Generated response with {len(sources)} sources")
            return generated_text, sources
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback_response = self._generate_fallback_response(query)
            return fallback_response, []
    
    def _prepare_context(self, results: List[Dict[str, Any]]) -> str:
        """Prepare context text from search results"""
        if not results:
            return "No relevant context found in the knowledge base."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            book = result['metadata'].get('book_title', 'Unknown Book')
            chapter = result['metadata'].get('chapter', 'Unknown Chapter')
            content = result['content'][:500]  # Limit context length
            
            context_parts.append(f"[Source {i}] From '{book}' - {chapter}:\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI"""
        return """You are Alex Hormozi AI, a business advisor based on Alex Hormozi's teachings and books. 

Your role:
- Provide practical, actionable business advice
- Focus on sales, marketing, operations, and scaling strategies
- Use Alex Hormozi's frameworks and methodologies
- Be direct, results-oriented, and value-driven
- Always cite your sources when referencing specific concepts

Guidelines:
- Answer based ONLY on the provided context from Alex Hormozi's books
- If the context doesn't contain relevant information, say so honestly
- Use specific examples and frameworks when available
- Be conversational but professional
- Focus on implementation and results

Remember: You're helping entrepreneurs build better businesses using proven strategies."""
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build the user prompt with query and context"""
        return f"""Based on Alex Hormozi's teachings in the provided context, please answer this question:

Question: {query}

Context from Alex Hormozi's books:
{context}

Please provide a helpful, actionable response based on the context above. If the context doesn't contain enough information to fully answer the question, please say so and provide what guidance you can."""
    
    def _prepare_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare source citations from search results"""
        sources = []
        for result in results:
            metadata = result['metadata']
            sources.append({
                'book': metadata.get('book_title', 'Unknown'),
                'chapter': metadata.get('chapter', 'Unknown'),
                'page': metadata.get('page_number', 0),
                'text_snippet': result['content'][:200] + "..." if len(result['content']) > 200 else result['content'],
                'similarity': round(result['similarity'], 3)
            })
        return sources
    
    def _generate_fallback_response(self, query: str) -> str:
        """Generate a fallback response when the main system fails"""
        return f"""I apologize, but I'm currently unable to access Alex Hormozi's knowledge base to answer your question about: "{query}"

This could be because:
1. The knowledge base hasn't been set up yet
2. There's a temporary technical issue
3. Your question might need to be rephrased

To get the best results, try:
- Being more specific about what aspect of business you're asking about
- Asking about topics covered in Alex Hormozi's books like offers, lead generation, or scaling
- Checking back later if this is a technical issue

I'm designed to provide business advice based on Alex Hormozi's proven strategies and frameworks."""

class KnowledgeBaseManager:
    """Manages knowledge base operations and health checks"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the knowledge base"""
        status = {
            'knowledge_base_available': False,
            'total_documents': 0,
            'collection_name': self.rag_service.collection_name,
            'chroma_path': str(self.rag_service.chroma_path),
            'books_available': [],
            'last_updated': None
        }
        
        try:
            if self.rag_service.is_knowledge_base_available():
                status['knowledge_base_available'] = True
                status['total_documents'] = self.rag_service.collection.count()
                
                # Get sample documents to identify available books
                sample = self.rag_service.collection.get(limit=100)
                if sample['metadatas']:
                    books = set()
                    for metadata in sample['metadatas']:
                        if metadata.get('book_title'):
                            books.add(metadata['book_title'])
                    status['books_available'] = list(books)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            status['error'] = str(e)
        
        return status
    
    def get_available_books(self) -> List[Dict[str, Any]]:
        """Get list of available books in the knowledge base"""
        if not self.rag_service.is_knowledge_base_available():
            return []
        
        try:
            # Get all documents to analyze available books
            all_docs = self.rag_service.collection.get(include=['metadatas'])
            
            books = {}
            for metadata in all_docs['metadatas']:
                book_title = metadata.get('book_title', 'Unknown')
                chapter = metadata.get('chapter', 'Unknown')
                
                if book_title not in books:
                    books[book_title] = {
                        'title': book_title,
                        'author': 'Alex Hormozi',
                        'chapters': set(),
                        'total_chunks': 0,
                        'status': 'available'
                    }
                
                books[book_title]['chapters'].add(chapter)
                books[book_title]['total_chunks'] += 1
            
            # Convert sets to lists for JSON serialization
            result = []
            for book_data in books.values():
                book_data['chapters'] = list(book_data['chapters'])
                result.append(book_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting available books: {e}")
            return []

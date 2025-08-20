from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import our services
from app.services.rag_service import RAGService, KnowledgeBaseManager
from app.config import settings

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Hormozi AI Business Advisor API",
    description="RAG-based AI assistant for business advice based on Alex Hormozi's teachings",
    version="1.0.0"
)

# Initialize RAG service
rag_service = RAGService(
    chroma_path=settings.chroma_persist_directory,
    collection_name=settings.collection_name,
    openai_api_key=settings.openai_api_key,
    model=settings.openai_model,
    temperature=settings.temperature
)

# Initialize knowledge base manager
kb_manager = KnowledgeBaseManager(rag_service)

# Configure CORS origins
cors_origins = ["http://localhost:3000", "http://localhost:5173"]  # Development
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    cors_origins.append(frontend_url)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins + ["https://*.vercel.app"],  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]
    conversation_id: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="healthy", 
        message="Hormozi AI Business Advisor API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy", 
        message="API is operational"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Main chat endpoint for business advice using RAG
    """
    try:
        # Check if knowledge base is available
        if not rag_service.is_knowledge_base_available():
            return ChatResponse(
                response="I'm sorry, but the knowledge base is not currently available. Please make sure the Alex Hormozi books have been processed and the vector database has been created. You can do this by running the training pipeline with your OpenAI API key.",
                sources=[{
                    "book": "System",
                    "chapter": "Setup Required",
                    "page": 0,
                    "text_snippet": "Knowledge base needs to be initialized. Please run: python scripts/run_pipeline.py --books_dir backend/data/raw --output_dir backend/data/chroma"
                }],
                conversation_id=message.conversation_id or "setup_required"
            )
        
        # Search for relevant context
        context_results = rag_service.search_knowledge_base(
            query=message.message,
            n_results=5,
            min_similarity=0.6
        )
        
        # Generate response using RAG
        response_text, sources = rag_service.generate_response(
            query=message.message,
            context_results=context_results
        )
        
        return ChatResponse(
            response=response_text,
            sources=sources,
            conversation_id=message.conversation_id or f"chat_{hash(message.message) % 10000}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/books")
async def get_available_books():
    """
    Get list of available books and their metadata
    """
    try:
        books = kb_manager.get_available_books()
        
        if not books:
            return {
                "books": [],
                "message": "No books available. Please run the knowledge training pipeline first.",
                "setup_required": True
            }
        
        return {"books": books}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving books: {str(e)}")

@app.post("/search")
async def semantic_search(query: str, limit: int = 5):
    """
    Perform semantic search across the knowledge base
    """
    try:
        if not rag_service.is_knowledge_base_available():
            return {
                "query": query,
                "results": [],
                "message": "Knowledge base not available. Please run the training pipeline first."
            }
        
        # Search the knowledge base
        results = rag_service.search_knowledge_base(
            query=query,
            n_results=limit,
            min_similarity=0.5
        )
        
        # Format results for response
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
                "book": result['book'],
                "chapter": result['chapter'],
                "page_number": result['page_number'],
                "similarity": result['similarity']
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/knowledge-status")
async def knowledge_base_status():
    """
    Get the current status of the knowledge base
    """
    try:
        status = kb_manager.health_check()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


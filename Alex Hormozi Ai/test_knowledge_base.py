#!/usr/bin/env python3
"""
Quick test script for the Hormozi AI knowledge base

This script helps you verify that your knowledge base is working correctly
before deployment.
"""

import os
import sys
from pathlib import Path

# Add the backend to the path
backend_path = Path(__file__).parent / "backend"
sys.path.append(str(backend_path))

try:
    from app.services.rag_service import RAGService, KnowledgeBaseManager
    from app.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root and have installed dependencies")
    sys.exit(1)

def test_knowledge_base():
    """Test the knowledge base functionality"""
    print("🧪 Testing Hormozi AI Knowledge Base")
    print("=" * 50)
    
    # Initialize RAG service
    try:
        rag_service = RAGService(
            chroma_path="backend/data/chroma",
            collection_name="hormozi_knowledge"
        )
        kb_manager = KnowledgeBaseManager(rag_service)
    except Exception as e:
        print(f"❌ Failed to initialize RAG service: {e}")
        return False
    
    # Test 1: Check if knowledge base is available
    print("\n1️⃣ Testing knowledge base availability...")
    if rag_service.is_knowledge_base_available():
        print("✅ Knowledge base is available")
    else:
        print("❌ Knowledge base not found")
        print("   Please run the training pipeline first:")
        print("   python scripts/run_pipeline.py --books_dir backend/data/raw --output_dir backend/data/chroma")
        return False
    
    # Test 2: Get knowledge base stats
    print("\n2️⃣ Getting knowledge base statistics...")
    try:
        status = kb_manager.health_check()
        print(f"✅ Total documents: {status['total_documents']}")
        print(f"✅ Available books: {', '.join(status['books_available'])}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return False
    
    # Test 3: Test search functionality
    print("\n3️⃣ Testing search functionality...")
    test_queries = [
        "How do I create an irresistible offer?",
        "What are the best lead generation strategies?",
        "How should I scale my business?"
    ]
    
    for query in test_queries:
        try:
            print(f"\n   Query: '{query}'")
            results = rag_service.search_knowledge_base(query, n_results=3)
            if results:
                print(f"   ✅ Found {len(results)} relevant results")
                print(f"   📖 Top result from: {results[0]['book']} - {results[0]['chapter']}")
            else:
                print(f"   ⚠️  No results found")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
            return False
    
    # Test 4: Test response generation
    print("\n4️⃣ Testing response generation...")
    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("   ⚠️  OpenAI API key not found - skipping response generation test")
            print("   Set OPENAI_API_KEY environment variable to test full functionality")
        else:
            print("   Testing with query: 'What makes an offer irresistible?'")
            context_results = rag_service.search_knowledge_base("What makes an offer irresistible?", n_results=3)
            response, sources = rag_service.generate_response(
                "What makes an offer irresistible?",
                context_results
            )
            print(f"   ✅ Generated response ({len(response)} characters)")
            print(f"   ✅ Found {len(sources)} source citations")
    except Exception as e:
        print(f"   ❌ Response generation error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your knowledge base is ready.")
    return True

def main():
    """Main function"""
    print("Hormozi AI Knowledge Base Test")
    print("Make sure you've run the training pipeline first!")
    print()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("   Some tests will be skipped")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    success = test_knowledge_base()
    
    if success:
        print("\n✅ Your Hormozi AI is ready for deployment!")
        print("   Next steps:")
        print("   1. Deploy backend to Railway")
        print("   2. Deploy frontend to Vercel") 
        print("   3. Start getting AI-powered business advice!")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        print("   See KNOWLEDGE_SETUP_GUIDE.md for detailed instructions")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Vector Database Setup Script for Hormozi AI Business Advisor

This script provides utilities for managing the ChromaDB vector database,
including initialization, querying, and maintenance operations.

Usage:
    python setup_vector_db.py --action init --db_path ../backend/data/chroma
    python setup_vector_db.py --action query --query "How to create offers?" --db_path ../backend/data/chroma
    python setup_vector_db.py --action stats --db_path ../backend/data/chroma

Features:
    - Database initialization and validation
    - Semantic search testing
    - Collection statistics and health checks
    - Data export and backup utilities
"""

import os
import json
import argparse
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorDBManager:
    """Manages vector database operations and utilities"""
    
    def __init__(self, db_path: str, collection_name: str = "hormozi_knowledge"):
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        if not self.db_path.exists():
            logger.error(f"Database path does not exist: {db_path}")
            raise FileNotFoundError(f"Database path not found: {db_path}")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Connected to collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to connect to collection {collection_name}: {e}")
            self.collection = None
    
    def initialize_database(self) -> bool:
        """Initialize and validate the vector database"""
        logger.info("Initializing vector database...")
        
        try:
            # List all collections
            collections = self.client.list_collections()
            logger.info(f"Available collections: {[c.name for c in collections]}")
            
            if not collections:
                logger.warning("No collections found in database")
                return False
            
            # Validate main collection
            if self.collection:
                count = self.collection.count()
                logger.info(f"Collection '{self.collection_name}' contains {count} items")
                
                if count > 0:
                    # Test a sample query
                    sample = self.collection.get(limit=1)
                    if sample['documents']:
                        logger.info("Database validation successful")
                        return True
                else:
                    logger.warning("Collection is empty")
                    return False
            else:
                logger.error("Could not access main collection")
                return False
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the collection"""
        if not self.collection:
            return {"error": "Collection not available"}
        
        try:
            count = self.collection.count()
            
            if count == 0:
                return {
                    "total_documents": 0,
                    "message": "Collection is empty"
                }
            
            # Get all metadata to analyze
            all_data = self.collection.get(include=['metadatas'])
            metadatas = all_data['metadatas']
            
            # Analyze metadata
            books = {}
            chapters = set()
            total_words = 0
            total_chars = 0
            
            for metadata in metadatas:
                book_title = metadata.get('book_title', 'Unknown')
                chapter = metadata.get('chapter', 'Unknown')
                word_count = metadata.get('word_count', 0)
                char_count = metadata.get('char_count', 0)
                
                if book_title not in books:
                    books[book_title] = {
                        'chapters': set(),
                        'chunk_count': 0,
                        'word_count': 0,
                        'char_count': 0
                    }
                
                books[book_title]['chapters'].add(chapter)
                books[book_title]['chunk_count'] += 1
                books[book_title]['word_count'] += word_count
                books[book_title]['char_count'] += char_count
                
                chapters.add(f"{book_title} - {chapter}")
                total_words += word_count
                total_chars += char_count
            
            # Convert sets to lists for JSON serialization
            for book_data in books.values():
                book_data['chapters'] = list(book_data['chapters'])
            
            stats = {
                "total_documents": count,
                "total_words": total_words,
                "total_characters": total_chars,
                "unique_books": len(books),
                "unique_chapters": len(chapters),
                "books_detail": books,
                "average_words_per_chunk": total_words / count if count > 0 else 0,
                "average_chars_per_chunk": total_chars / count if count > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def semantic_search(self, query: str, n_results: int = 5, 
                       filter_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform semantic search on the collection"""
        if not self.collection:
            return {"error": "Collection not available"}
        
        try:
            logger.info(f"Searching for: '{query}'")
            
            search_kwargs = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }
            
            if filter_metadata:
                search_kwargs["where"] = filter_metadata
            
            results = self.collection.query(**search_kwargs)
            
            # Format results
            formatted_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        "document": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None,
                        "similarity_score": 1 - results['distances'][0][i] if results['distances'] else None
                    }
                    formatted_results.append(result)
            
            return {
                "query": query,
                "n_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"error": str(e)}
    
    def export_collection(self, output_file: str) -> bool:
        """Export collection data to JSON file"""
        if not self.collection:
            logger.error("Collection not available for export")
            return False
        
        try:
            logger.info(f"Exporting collection to: {output_file}")
            
            # Get all data
            all_data = self.collection.get(include=['documents', 'metadatas', 'embeddings'])
            
            export_data = {
                "collection_name": self.collection_name,
                "total_documents": len(all_data['ids']),
                "export_timestamp": str(pd.Timestamp.now()),
                "data": {
                    "ids": all_data['ids'],
                    "documents": all_data['documents'],
                    "metadatas": all_data['metadatas'],
                    # Note: embeddings are large, only export if specifically needed
                    # "embeddings": all_data['embeddings']
                }
            }
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Export completed: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
    
    def test_search_functionality(self) -> bool:
        """Test search functionality with sample queries"""
        if not self.collection:
            logger.error("Collection not available for testing")
            return False
        
        test_queries = [
            "How to create irresistible offers?",
            "Lead generation strategies",
            "Sales process optimization",
            "Business scaling techniques",
            "Pricing strategies"
        ]
        
        logger.info("Testing search functionality...")
        
        all_tests_passed = True
        
        for query in test_queries:
            try:
                results = self.semantic_search(query, n_results=3)
                
                if "error" in results:
                    logger.error(f"Search failed for '{query}': {results['error']}")
                    all_tests_passed = False
                elif results['n_results'] == 0:
                    logger.warning(f"No results found for '{query}'")
                    all_tests_passed = False
                else:
                    logger.info(f"✓ Query '{query}' returned {results['n_results']} results")
                    
                    # Log top result
                    if results['results']:
                        top_result = results['results'][0]
                        logger.info(f"  Top result: {top_result['document'][:100]}...")
                        logger.info(f"  From: {top_result['metadata'].get('book_title', 'Unknown')} - {top_result['metadata'].get('chapter', 'Unknown')}")
                        logger.info(f"  Similarity: {top_result['similarity_score']:.3f}")
                
            except Exception as e:
                logger.error(f"Test failed for '{query}': {e}")
                all_tests_passed = False
        
        if all_tests_passed:
            logger.info("✓ All search tests passed")
        else:
            logger.warning("⚠ Some search tests failed")
        
        return all_tests_passed

def main():
    parser = argparse.ArgumentParser(description='Manage Hormozi AI vector database')
    parser.add_argument('--action', required=True, 
                       choices=['init', 'stats', 'query', 'export', 'test'],
                       help='Action to perform')
    parser.add_argument('--db_path', required=True, help='Path to ChromaDB database')
    parser.add_argument('--collection_name', default='hormozi_knowledge', 
                       help='Collection name')
    parser.add_argument('--query', help='Search query (for query action)')
    parser.add_argument('--n_results', type=int, default=5, 
                       help='Number of results to return (for query action)')
    parser.add_argument('--output_file', help='Output file path (for export action)')
    parser.add_argument('--filter_book', help='Filter results by book title')
    
    args = parser.parse_args()
    
    # Initialize database manager
    try:
        db_manager = VectorDBManager(args.db_path, args.collection_name)
    except FileNotFoundError as e:
        logger.error(str(e))
        return
    
    # Perform requested action
    if args.action == 'init':
        success = db_manager.initialize_database()
        if success:
            logger.info("Database initialization successful")
        else:
            logger.error("Database initialization failed")
    
    elif args.action == 'stats':
        stats = db_manager.get_collection_stats()
        print("\n" + "="*50)
        print("COLLECTION STATISTICS")
        print("="*50)
        
        if "error" in stats:
            print(f"Error: {stats['error']}")
        else:
            print(f"Total Documents: {stats['total_documents']}")
            print(f"Total Words: {stats['total_words']:,}")
            print(f"Total Characters: {stats['total_characters']:,}")
            print(f"Unique Books: {stats['unique_books']}")
            print(f"Unique Chapters: {stats['unique_chapters']}")
            print(f"Avg Words/Chunk: {stats['average_words_per_chunk']:.1f}")
            print(f"Avg Chars/Chunk: {stats['average_chars_per_chunk']:.1f}")
            
            print("\nBooks Detail:")
            for book_title, book_data in stats['books_detail'].items():
                print(f"  📖 {book_title}:")
                print(f"    Chunks: {book_data['chunk_count']}")
                print(f"    Words: {book_data['word_count']:,}")
                print(f"    Chapters: {len(book_data['chapters'])}")
    
    elif args.action == 'query':
        if not args.query:
            logger.error("Query string is required for query action")
            return
        
        filter_metadata = None
        if args.filter_book:
            filter_metadata = {"book_title": args.filter_book}
        
        results = db_manager.semantic_search(
            args.query, 
            args.n_results, 
            filter_metadata
        )
        
        print("\n" + "="*50)
        print(f"SEARCH RESULTS FOR: '{args.query}'")
        print("="*50)
        
        if "error" in results:
            print(f"Error: {results['error']}")
        elif results['n_results'] == 0:
            print("No results found")
        else:
            for i, result in enumerate(results['results'], 1):
                print(f"\n{i}. Similarity: {result['similarity_score']:.3f}")
                print(f"   Book: {result['metadata'].get('book_title', 'Unknown')}")
                print(f"   Chapter: {result['metadata'].get('chapter', 'Unknown')}")
                print(f"   Content: {result['document'][:200]}...")
                if len(result['document']) > 200:
                    print("   [truncated]")
    
    elif args.action == 'export':
        if not args.output_file:
            args.output_file = f"{args.collection_name}_export.json"
        
        success = db_manager.export_collection(args.output_file)
        if success:
            logger.info("Export completed successfully")
        else:
            logger.error("Export failed")
    
    elif args.action == 'test':
        success = db_manager.test_search_functionality()
        if success:
            logger.info("All tests passed ✓")
        else:
            logger.warning("Some tests failed ⚠")

if __name__ == "__main__":
    main()


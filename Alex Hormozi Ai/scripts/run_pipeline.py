#!/usr/bin/env python3
"""
Complete Data Pipeline Runner for Hormozi AI Business Advisor

This script runs the complete data processing pipeline from raw books to vector database.
It handles the entire workflow: text extraction -> chunking -> embedding generation -> vector storage.

Usage:
    python run_pipeline.py --books_dir ../backend/data/raw --output_dir ../backend/data/chroma

Features:
    - End-to-end pipeline automation
    - Progress tracking and logging
    - Error handling and recovery
    - Validation at each step
    - Performance monitoring
"""

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add scripts directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processing import BookProcessor
from create_embeddings import EmbeddingGenerator, ChromaDBManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HormoziPipeline:
    """Complete pipeline for processing Hormozi books into vector database"""
    
    def __init__(self, books_dir: str, output_dir: str, 
                 embedding_model: str = "openai", chunk_size: int = 1000):
        self.books_dir = Path(books_dir)
        self.output_dir = Path(output_dir)
        self.processed_dir = self.output_dir.parent / "processed"
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        
        # Create directories
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.book_processor = BookProcessor(chunk_size=chunk_size, chunk_overlap=200)
        self.embedding_generator = None
        self.chroma_manager = None
        
        # Pipeline state
        self.pipeline_state = {
            'start_time': None,
            'end_time': None,
            'books_found': 0,
            'books_processed': 0,
            'total_chunks': 0,
            'embeddings_created': 0,
            'vector_db_populated': False,
            'errors': []
        }
    
    def find_books(self) -> List[Path]:
        """Find all supported book files in the books directory"""
        logger.info(f"Scanning for books in: {self.books_dir}")
        
        book_files = []
        for ext in ['*.pdf', '*.epub']:
            book_files.extend(self.books_dir.glob(ext))
        
        self.pipeline_state['books_found'] = len(book_files)
        
        if not book_files:
            logger.error(f"No book files found in {self.books_dir}")
            logger.info("Supported formats: PDF, EPUB")
            logger.info("Please place Alex Hormozi's books in the books directory")
            return []
        
        logger.info(f"Found {len(book_files)} book(s):")
        for book in book_files:
            logger.info(f"  📖 {book.name}")
        
        return book_files
    
    def process_books(self, book_files: List[Path]) -> List[Dict[str, Any]]:
        """Process all books into text chunks"""
        logger.info("Starting book processing...")
        
        all_chunks = []
        processed_count = 0
        
        for book_file in book_files:
            try:
                logger.info(f"Processing: {book_file.name}")
                chunks = self.book_processor.process_book(str(book_file), str(self.processed_dir))
                
                if chunks:
                    all_chunks.extend([chunk.__dict__ for chunk in chunks])
                    processed_count += 1
                    logger.info(f"✓ Created {len(chunks)} chunks from {book_file.name}")
                else:
                    logger.warning(f"⚠ No chunks created from {book_file.name}")
                    self.pipeline_state['errors'].append(f"Failed to process {book_file.name}")
                
            except Exception as e:
                logger.error(f"✗ Error processing {book_file.name}: {e}")
                self.pipeline_state['errors'].append(f"Error processing {book_file.name}: {str(e)}")
        
        self.pipeline_state['books_processed'] = processed_count
        self.pipeline_state['total_chunks'] = len(all_chunks)
        
        # Save processed chunks
        chunks_file = self.processed_dir / 'processed_chunks.json'
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(all_chunks)} chunks to {chunks_file}")
        return all_chunks
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> bool:
        """Generate embeddings for all chunks"""
        logger.info("Starting embedding generation...")
        
        try:
            # Initialize embedding generator
            self.embedding_generator = EmbeddingGenerator(
                self.embedding_model,
                "text-embedding-ada-002" if self.embedding_model == "openai" else "all-MiniLM-L6-v2"
            )
            
            # Extract texts
            texts = [chunk['content'] for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.embedding_generator.generate_embeddings_batch(texts, batch_size=50)
            
            self.pipeline_state['embeddings_created'] = len(embeddings)
            logger.info(f"Created {len(embeddings)} embeddings")
            
            return len(embeddings) == len(chunks)
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            self.pipeline_state['errors'].append(f"Embedding generation failed: {str(e)}")
            return False
    
    def populate_vector_db(self, chunks: List[Dict[str, Any]]) -> bool:
        """Populate ChromaDB with chunks and embeddings"""
        logger.info("Populating vector database...")
        
        try:
            # Initialize ChromaDB manager
            self.chroma_manager = ChromaDBManager(str(self.output_dir), "hormozi_knowledge")
            
            # Generate embeddings if not already done
            if not self.embedding_generator:
                if not self.create_embeddings(chunks):
                    return False
            
            # Extract texts and generate embeddings
            texts = [chunk['content'] for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(texts, batch_size=50)
            
            # Add to ChromaDB
            self.chroma_manager.add_embeddings(chunks, embeddings)
            
            self.pipeline_state['vector_db_populated'] = True
            logger.info("Vector database populated successfully")
            
            # Get and log statistics
            stats = self.chroma_manager.get_collection_stats()
            logger.info(f"Database contains {stats['total_chunks']} chunks from {stats['unique_books']} books")
            
            return True
            
        except Exception as e:
            logger.error(f"Error populating vector database: {e}")
            self.pipeline_state['errors'].append(f"Vector database population failed: {str(e)}")
            return False
    
    def validate_pipeline(self) -> bool:
        """Validate the complete pipeline"""
        logger.info("Validating pipeline results...")
        
        try:
            if not self.chroma_manager:
                self.chroma_manager = ChromaDBManager(str(self.output_dir), "hormozi_knowledge")
            
            # Test search functionality
            test_queries = [
                "How to create irresistible offers?",
                "Lead generation strategies",
                "Business scaling"
            ]
            
            all_tests_passed = True
            
            for query in test_queries:
                try:
                    results = self.chroma_manager.collection.query(
                        query_texts=[query],
                        n_results=3,
                        include=["documents", "metadatas", "distances"]
                    )
                    
                    if not results['documents'] or not results['documents'][0]:
                        logger.warning(f"No results for test query: '{query}'")
                        all_tests_passed = False
                    else:
                        logger.info(f"✓ Test query '{query}' returned {len(results['documents'][0])} results")
                        
                except Exception as e:
                    logger.error(f"Test query failed: '{query}' - {e}")
                    all_tests_passed = False
            
            if all_tests_passed:
                logger.info("✓ Pipeline validation successful")
            else:
                logger.warning("⚠ Some validation tests failed")
                
            return all_tests_passed
            
        except Exception as e:
            logger.error(f"Pipeline validation failed: {e}")
            return False
    
    def run_complete_pipeline(self) -> bool:
        """Run the complete pipeline from books to vector database"""
        logger.info("🚀 Starting Hormozi AI Pipeline")
        logger.info("="*60)
        
        self.pipeline_state['start_time'] = time.time()
        
        try:
            # Step 1: Find books
            book_files = self.find_books()
            if not book_files:
                return False
            
            # Step 2: Process books
            chunks = self.process_books(book_files)
            if not chunks:
                logger.error("No chunks were created from the books")
                return False
            
            # Step 3: Create embeddings and populate database
            if not self.populate_vector_db(chunks):
                logger.error("Failed to populate vector database")
                return False
            
            # Step 4: Validate pipeline
            validation_passed = self.validate_pipeline()
            
            self.pipeline_state['end_time'] = time.time()
            
            # Generate final report
            self.generate_report()
            
            if validation_passed:
                logger.info("🎉 Pipeline completed successfully!")
                return True
            else:
                logger.warning("⚠ Pipeline completed with warnings")
                return False
                
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.pipeline_state['errors'].append(f"Pipeline failure: {str(e)}")
            self.pipeline_state['end_time'] = time.time()
            self.generate_report()
            return False
    
    def generate_report(self):
        """Generate a comprehensive pipeline report"""
        duration = (self.pipeline_state['end_time'] - self.pipeline_state['start_time']) / 60
        
        report = {
            "pipeline_summary": {
                "duration_minutes": round(duration, 2),
                "books_found": self.pipeline_state['books_found'],
                "books_processed": self.pipeline_state['books_processed'],
                "total_chunks": self.pipeline_state['total_chunks'],
                "embeddings_created": self.pipeline_state['embeddings_created'],
                "vector_db_populated": self.pipeline_state['vector_db_populated'],
                "errors": self.pipeline_state['errors']
            },
            "configuration": {
                "books_directory": str(self.books_dir),
                "output_directory": str(self.output_dir),
                "embedding_model": self.embedding_model,
                "chunk_size": self.chunk_size
            },
            "timestamp": time.time()
        }
        
        # Save report
        report_file = self.output_dir.parent / 'pipeline_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Log summary
        logger.info("="*60)
        logger.info("📊 PIPELINE REPORT")
        logger.info("="*60)
        logger.info(f"Duration: {duration:.2f} minutes")
        logger.info(f"Books found: {self.pipeline_state['books_found']}")
        logger.info(f"Books processed: {self.pipeline_state['books_processed']}")
        logger.info(f"Total chunks: {self.pipeline_state['total_chunks']}")
        logger.info(f"Embeddings created: {self.pipeline_state['embeddings_created']}")
        logger.info(f"Vector DB populated: {self.pipeline_state['vector_db_populated']}")
        
        if self.pipeline_state['errors']:
            logger.warning(f"Errors encountered: {len(self.pipeline_state['errors'])}")
            for error in self.pipeline_state['errors']:
                logger.warning(f"  - {error}")
        
        logger.info(f"Report saved to: {report_file}")

def main():
    parser = argparse.ArgumentParser(description='Run complete Hormozi AI pipeline')
    parser.add_argument('--books_dir', required=True, help='Directory containing book files')
    parser.add_argument('--output_dir', required=True, help='ChromaDB output directory')
    parser.add_argument('--embedding_model', choices=['openai', 'sentence_transformer'], 
                       default='openai', help='Embedding model to use')
    parser.add_argument('--chunk_size', type=int, default=1000, help='Chunk size in words')
    parser.add_argument('--validate_only', action='store_true', 
                       help='Only validate existing database')
    
    args = parser.parse_args()
    
    # Check OpenAI API key if using OpenAI embeddings
    if args.embedding_model == 'openai' and not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
        logger.info("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Initialize pipeline
    pipeline = HormoziPipeline(
        books_dir=args.books_dir,
        output_dir=args.output_dir,
        embedding_model=args.embedding_model,
        chunk_size=args.chunk_size
    )
    
    if args.validate_only:
        # Only run validation
        logger.info("Running validation only...")
        success = pipeline.validate_pipeline()
        if success:
            logger.info("✅ Validation passed")
        else:
            logger.error("❌ Validation failed")
    else:
        # Run complete pipeline
        success = pipeline.run_complete_pipeline()
        
        if success:
            logger.info("✅ Pipeline completed successfully!")
            logger.info("You can now start the backend server and begin using the AI advisor.")
        else:
            logger.error("❌ Pipeline failed. Check the logs for details.")
            sys.exit(1)

if __name__ == "__main__":
    main()


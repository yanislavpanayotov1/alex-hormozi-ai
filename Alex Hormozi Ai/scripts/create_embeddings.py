#!/usr/bin/env python3
"""
Embedding Generation Script for Hormozi AI Business Advisor

This script creates embeddings from processed text chunks and stores them in ChromaDB.
It supports both OpenAI embeddings and local sentence transformers.

Usage:
    python create_embeddings.py --input_file ../backend/data/processed/processed_chunks.json --output_dir ../backend/data/chroma

Features:
    - OpenAI Ada-002 embeddings
    - Local sentence transformer embeddings
    - ChromaDB vector storage
    - Batch processing for efficiency
    - Progress tracking and error handling
"""

import os
import json
import argparse
import logging
from typing import List, Dict, Any
from pathlib import Path
import time

import openai
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Handles embedding generation and vector database operations"""
    
    def __init__(self, embedding_model: str = "openai", model_name: str = "text-embedding-ada-002"):
        self.embedding_model = embedding_model
        self.model_name = model_name
        
        if embedding_model == "openai":
            self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif embedding_model == "sentence_transformer":
            logger.info(f"Loading sentence transformer model: {model_name}")
            self.st_model = SentenceTransformer(model_name)
        else:
            raise ValueError(f"Unsupported embedding model: {embedding_model}")
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i + batch_size]
            
            if self.embedding_model == "openai":
                embeddings = self._generate_openai_embeddings(batch)
            else:
                embeddings = self._generate_st_embeddings(batch)
            
            all_embeddings.extend(embeddings)
            
            # Rate limiting for OpenAI
            if self.embedding_model == "openai":
                time.sleep(0.1)
        
        return all_embeddings
    
    def _generate_openai_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * 1536 for _ in texts]  # Ada-002 has 1536 dimensions
    
    def _generate_st_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence transformers"""
        try:
            embeddings = self.st_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating sentence transformer embeddings: {e}")
            # Return zero embeddings as fallback
            embedding_dim = self.st_model.get_sentence_embedding_dimension()
            return [[0.0] * embedding_dim for _ in texts]

class ChromaDBManager:
    """Manages ChromaDB operations"""
    
    def __init__(self, persist_directory: str, collection_name: str = "hormozi_knowledge"):
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Alex Hormozi business knowledge base"}
            )
            logger.info(f"Created new collection: {collection_name}")
    
    def add_embeddings(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add embeddings to ChromaDB collection"""
        logger.info(f"Adding {len(chunks)} embeddings to ChromaDB...")
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in chunks]
        documents = [chunk['content'] for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            metadata = {
                'book_title': chunk['book_title'],
                'chapter': chunk['chapter'],
                'page_number': chunk['page_number'],
                'word_count': chunk['word_count'],
                'char_count': chunk['char_count'],
                'chunk_index': chunk['chunk_index'],
                'source_file': chunk['source_file']
            }
            metadatas.append(metadata)
        
        # Add to collection in batches
        batch_size = 100
        for i in tqdm(range(0, len(chunks), batch_size), desc="Adding to ChromaDB"):
            end_idx = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        logger.info("Successfully added all embeddings to ChromaDB")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        
        # Get sample of metadata to analyze
        sample_size = min(100, count)
        if count > 0:
            sample = self.collection.get(limit=sample_size)
            books = set()
            chapters = set()
            
            for metadata in sample['metadatas']:
                books.add(metadata.get('book_title', 'Unknown'))
                chapters.add(f"{metadata.get('book_title', 'Unknown')} - {metadata.get('chapter', 'Unknown')}")
        else:
            books = set()
            chapters = set()
        
        return {
            'total_chunks': count,
            'unique_books': len(books),
            'unique_chapters': len(chapters),
            'books': list(books),
            'sample_chapters': list(chapters)[:10]  # First 10 chapters as sample
        }

def main():
    parser = argparse.ArgumentParser(description='Generate embeddings for Hormozi AI')
    parser.add_argument('--input_file', required=True, help='Path to processed chunks JSON file')
    parser.add_argument('--output_dir', required=True, help='ChromaDB output directory')
    parser.add_argument('--embedding_model', choices=['openai', 'sentence_transformer'], 
                       default='openai', help='Embedding model to use')
    parser.add_argument('--model_name', default='text-embedding-ada-002', 
                       help='Specific model name (for OpenAI or sentence transformer)')
    parser.add_argument('--collection_name', default='hormozi_knowledge', 
                       help='ChromaDB collection name')
    parser.add_argument('--batch_size', type=int, default=100, 
                       help='Batch size for embedding generation')
    parser.add_argument('--reset_collection', action='store_true', 
                       help='Reset existing collection before adding new data')
    
    args = parser.parse_args()
    
    # Load processed chunks
    input_file = Path(args.input_file)
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return
    
    logger.info(f"Loading chunks from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} chunks")
    
    # Initialize embedding generator
    if args.embedding_model == 'openai' and not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
        return
    
    embedding_generator = EmbeddingGenerator(args.embedding_model, args.model_name)
    
    # Initialize ChromaDB manager
    chroma_manager = ChromaDBManager(args.output_dir, args.collection_name)
    
    # Reset collection if requested
    if args.reset_collection:
        logger.info("Resetting collection...")
        chroma_manager.client.delete_collection(args.collection_name)
        chroma_manager.collection = chroma_manager.client.create_collection(
            name=args.collection_name,
            metadata={"description": "Alex Hormozi business knowledge base"}
        )
    
    # Extract texts for embedding
    texts = [chunk['content'] for chunk in chunks]
    
    # Generate embeddings
    logger.info(f"Generating embeddings using {args.embedding_model}...")
    embeddings = embedding_generator.generate_embeddings_batch(texts, args.batch_size)
    
    # Add to ChromaDB
    chroma_manager.add_embeddings(chunks, embeddings)
    
    # Get and display statistics
    stats = chroma_manager.get_collection_stats()
    logger.info("Collection Statistics:")
    logger.info(f"  Total chunks: {stats['total_chunks']}")
    logger.info(f"  Unique books: {stats['unique_books']}")
    logger.info(f"  Unique chapters: {stats['unique_chapters']}")
    logger.info(f"  Books: {', '.join(stats['books'])}")
    
    # Save embedding metadata
    metadata_file = Path(args.output_dir) / 'embedding_metadata.json'
    embedding_metadata = {
        'embedding_model': args.embedding_model,
        'model_name': args.model_name,
        'total_chunks': len(chunks),
        'embedding_dimensions': len(embeddings[0]) if embeddings else 0,
        'collection_name': args.collection_name,
        'creation_timestamp': time.time(),
        'statistics': stats
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(embedding_metadata, f, indent=2)
    
    logger.info(f"Embedding generation complete!")
    logger.info(f"ChromaDB collection: {args.collection_name}")
    logger.info(f"Metadata saved to: {metadata_file}")

if __name__ == "__main__":
    main()


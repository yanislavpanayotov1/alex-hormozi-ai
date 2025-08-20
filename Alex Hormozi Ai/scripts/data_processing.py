#!/usr/bin/env python3
"""
Data Processing Script for Hormozi AI Business Advisor

This script handles the extraction and preprocessing of text from Alex Hormozi's books.
It supports PDF and EPUB formats and prepares the text for embedding generation.

Usage:
    python data_processing.py --input_dir ../backend/data/raw --output_dir ../backend/data/processed

Features:
    - PDF text extraction with PyPDF2
    - EPUB text extraction with BeautifulSoup
    - Text cleaning (remove headers, footers, page numbers)
    - Smart chunking with semantic boundaries
    - Metadata extraction and preservation
"""

import os
import re
import json
import argparse
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

import PyPDF2
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    id: str
    content: str
    book_title: str
    chapter: str
    page_number: int
    word_count: int
    char_count: int
    chunk_index: int
    source_file: str

class BookProcessor:
    """Handles the processing of individual books"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.stop_words = set(stopwords.words('english'))
        
    def extract_pdf_text(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from PDF file, returning (text, page_number) tuples"""
        text_pages = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_pages.append((text, page_num))
                        
        except Exception as e:
            logger.error(f"Error extracting PDF {file_path}: {e}")
            
        return text_pages
    
    def extract_epub_text(self, file_path: str) -> List[Tuple[str, int]]:
        """Extract text from EPUB file"""
        # Note: This is a simplified EPUB extraction
        # For production, consider using ebooklib library
        text_pages = []
        
        try:
            import zipfile
            
            with zipfile.ZipFile(file_path, 'r') as epub:
                # Find HTML files in the EPUB
                html_files = [f for f in epub.namelist() if f.endswith('.html') or f.endswith('.xhtml')]
                
                for i, html_file in enumerate(html_files, 1):
                    try:
                        content = epub.read(html_file).decode('utf-8')
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text()
                        
                        if text.strip():
                            text_pages.append((text, i))
                            
                    except Exception as e:
                        logger.warning(f"Error processing {html_file} in {file_path}: {e}")
                        
        except Exception as e:
            logger.error(f"Error extracting EPUB {file_path}: {e}")
            
        return text_pages
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove common PDF artifacts
        text = re.sub(r'\\n+', ' ', text)
        text = re.sub(r'\\t+', ' ', text)
        
        # Remove page numbers (simple patterns)
        text = re.sub(r'\\b\\d+\\b(?=\\s*$)', '', text, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        text = re.sub(r'\\s+', ' ', text)
        
        # Remove common headers/footers patterns
        text = re.sub(r'^(Chapter|CHAPTER)\\s+\\d+.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\\d+\\s*$', '', text, flags=re.MULTILINE)  # Page numbers on their own line
        
        return text.strip()
    
    def extract_chapters(self, text: str) -> List[Tuple[str, str]]:
        """Extract chapters from text, returning (chapter_name, chapter_text) tuples"""
        # Simple chapter detection - can be improved based on book structure
        chapter_pattern = r'(Chapter|CHAPTER)\\s+(\\d+|[IVX]+)\\s*[:-]?\\s*([^\\n]*)'
        chapters = []
        
        chapter_matches = list(re.finditer(chapter_pattern, text))
        
        if not chapter_matches:
            # If no chapters found, treat entire text as one chapter
            return [("Full Text", text)]
        
        for i, match in enumerate(chapter_matches):
            chapter_num = match.group(2)
            chapter_title = match.group(3).strip() or f"Chapter {chapter_num}"
            
            start_pos = match.start()
            end_pos = chapter_matches[i + 1].start() if i + 1 < len(chapter_matches) else len(text)
            
            chapter_text = text[start_pos:end_pos]
            chapters.append((chapter_title, chapter_text))
            
        return chapters
    
    def create_chunks(self, text: str, book_title: str, chapter: str, 
                     page_number: int, source_file: str) -> List[TextChunk]:
        """Create overlapping chunks from text"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""
        current_word_count = 0
        chunk_index = 0
        
        for sentence in sentences:
            sentence_words = len(word_tokenize(sentence))
            
            if current_word_count + sentence_words > self.chunk_size and current_chunk:
                # Create chunk
                chunk = TextChunk(
                    id=f"{book_title.lower().replace(' ', '_')}_{chapter.lower().replace(' ', '_')}_{chunk_index}",
                    content=current_chunk.strip(),
                    book_title=book_title,
                    chapter=chapter,
                    page_number=page_number,
                    word_count=current_word_count,
                    char_count=len(current_chunk),
                    chunk_index=chunk_index,
                    source_file=source_file
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = sentences[max(0, len(sentences) - 3):len(sentences)]
                current_chunk = " ".join(overlap_sentences) + " " + sentence
                current_word_count = sum(len(word_tokenize(s)) for s in overlap_sentences) + sentence_words
                chunk_index += 1
            else:
                current_chunk += " " + sentence
                current_word_count += sentence_words
        
        # Add final chunk if it has content
        if current_chunk.strip():
            chunk = TextChunk(
                id=f"{book_title.lower().replace(' ', '_')}_{chapter.lower().replace(' ', '_')}_{chunk_index}",
                content=current_chunk.strip(),
                book_title=book_title,
                chapter=chapter,
                page_number=page_number,
                word_count=current_word_count,
                char_count=len(current_chunk),
                chunk_index=chunk_index,
                source_file=source_file
            )
            chunks.append(chunk)
            
        return chunks
    
    def process_book(self, file_path: str, output_dir: str) -> List[TextChunk]:
        """Process a single book file and return chunks"""
        logger.info(f"Processing book: {file_path}")
        
        file_path = Path(file_path)
        book_title = file_path.stem
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text_pages = self.extract_pdf_text(str(file_path))
        elif file_path.suffix.lower() == '.epub':
            text_pages = self.extract_epub_text(str(file_path))
        else:
            logger.error(f"Unsupported file format: {file_path.suffix}")
            return []
        
        if not text_pages:
            logger.warning(f"No text extracted from {file_path}")
            return []
        
        # Combine all pages
        full_text = " ".join([text for text, _ in text_pages])
        full_text = self.clean_text(full_text)
        
        # Extract chapters
        chapters = self.extract_chapters(full_text)
        
        all_chunks = []
        
        for chapter_name, chapter_text in chapters:
            # Create chunks for this chapter
            chunks = self.create_chunks(
                chapter_text, 
                book_title, 
                chapter_name, 
                1,  # We could map this to actual page numbers if needed
                str(file_path)
            )
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from {book_title}")
        return all_chunks

def main():
    parser = argparse.ArgumentParser(description='Process books for Hormozi AI')
    parser.add_argument('--input_dir', required=True, help='Directory containing book files')
    parser.add_argument('--output_dir', required=True, help='Output directory for processed chunks')
    parser.add_argument('--chunk_size', type=int, default=1000, help='Target chunk size in words')
    parser.add_argument('--chunk_overlap', type=int, default=200, help='Overlap between chunks in words')
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = BookProcessor(args.chunk_size, args.chunk_overlap)
    
    # Find book files
    book_files = []
    for ext in ['*.pdf', '*.epub']:
        book_files.extend(input_dir.glob(ext))
    
    if not book_files:
        logger.error(f"No book files found in {input_dir}")
        return
    
    all_chunks = []
    
    # Process each book
    for book_file in book_files:
        chunks = processor.process_book(book_file, str(output_dir))
        all_chunks.extend(chunks)
    
    # Save chunks to JSON
    chunks_file = output_dir / 'processed_chunks.json'
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(chunk) for chunk in all_chunks], f, indent=2, ensure_ascii=False)
    
    # Save metadata summary
    metadata_file = output_dir / 'processing_metadata.json'
    metadata = {
        'total_chunks': len(all_chunks),
        'books_processed': len(book_files),
        'book_files': [str(f) for f in book_files],
        'chunk_size': args.chunk_size,
        'chunk_overlap': args.chunk_overlap,
        'books_summary': {}
    }
    
    # Add per-book statistics
    for book_file in book_files:
        book_title = book_file.stem
        book_chunks = [c for c in all_chunks if c.book_title == book_title]
        metadata['books_summary'][book_title] = {
            'chunks': len(book_chunks),
            'total_words': sum(c.word_count for c in book_chunks),
            'total_chars': sum(c.char_count for c in book_chunks),
            'chapters': list(set(c.chapter for c in book_chunks))
        }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Processing complete! Created {len(all_chunks)} chunks from {len(book_files)} books")
    logger.info(f"Chunks saved to: {chunks_file}")
    logger.info(f"Metadata saved to: {metadata_file}")

if __name__ == "__main__":
    main()


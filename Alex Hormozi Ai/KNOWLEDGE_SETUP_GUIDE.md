# 📚 Alex Hormozi Knowledge Base Setup Guide

This guide will help you set up the Alex Hormozi knowledge base for your AI assistant. The system uses RAG (Retrieval-Augmented Generation) to provide accurate, source-cited business advice based on Alex Hormozi's books.

## 🎯 Overview

The knowledge training pipeline:
1. **Text Extraction**: Extracts text from Alex Hormozi's books (PDF/EPUB)
2. **Text Processing**: Cleans and chunks the text for optimal retrieval
3. **Embedding Generation**: Creates vector embeddings using OpenAI
4. **Vector Storage**: Stores embeddings in ChromaDB for fast similarity search
5. **RAG Integration**: Connects the knowledge base to the FastAPI backend

## 📋 Prerequisites

### Required
- **OpenAI API Key**: For embeddings and chat completions
- **Alex Hormozi's Books**: PDF or EPUB format
- **Python 3.9+**: For running the training pipeline

### Recommended Books
- **$100M Offers** - Core strategies for creating irresistible offers
- **$100M Leads** - Lead generation and customer acquisition
- **Gym Launch Secrets** - Scaling strategies and operations

## 🚀 Quick Setup (5 Steps)

### Step 1: Get Your Books
1. **Purchase** Alex Hormozi's books from legitimate sources:
   - [Amazon](https://amazon.com) (Kindle versions work)
   - [Official website](https://acquisition.com)
   - Other authorized retailers

2. **Convert to PDF/EPUB** if needed:
   - Use Calibre for format conversion
   - Ensure text is searchable (not image-based)

3. **Place books** in the raw data directory:
   ```bash
   mkdir -p backend/data/raw
   # Copy your book files here
   cp ~/Downloads/100M_Offers.pdf backend/data/raw/
   cp ~/Downloads/100M_Leads.pdf backend/data/raw/
   ```

### Step 2: Set Up Environment
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your_openai_api_key_here"

# Or create a .env file in the backend directory
cd backend
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### Step 3: Install Dependencies
```bash
# Install Python dependencies for training
pip install -r scripts/requirements.txt

# Or install backend requirements (includes training deps)
cd backend
pip install -r requirements.txt
```

### Step 4: Run the Training Pipeline
```bash
# From the project root directory
python scripts/run_pipeline.py \
  --books_dir backend/data/raw \
  --output_dir backend/data/chroma \
  --embedding_model openai \
  --chunk_size 1000
```

### Step 5: Verify Setup
```bash
# Test the knowledge base
python scripts/run_pipeline.py \
  --books_dir backend/data/raw \
  --output_dir backend/data/chroma \
  --validate_only
```

## 📊 Expected Results

After successful training, you should see:

```
📊 PIPELINE REPORT
==========================================
Duration: 15.32 minutes
Books found: 2
Books processed: 2
Total chunks: 1,247
Embeddings created: 1,247
Vector DB populated: True
```

## 🔧 Detailed Setup Instructions

### Manual Step-by-Step Process

If the quick setup doesn't work, try the manual approach:

#### 1. Data Processing
```bash
# Process books into text chunks
python scripts/data_processing.py \
  --input_dir backend/data/raw \
  --output_dir backend/data/processed \
  --chunk_size 1000 \
  --chunk_overlap 200
```

#### 2. Generate Embeddings
```bash
# Create embeddings and populate ChromaDB
python scripts/create_embeddings.py \
  --input_file backend/data/processed/processed_chunks.json \
  --output_dir backend/data/chroma \
  --embedding_model openai \
  --collection_name hormozi_knowledge
```

#### 3. Test the System
```bash
# Start the backend server
cd backend
uvicorn app.main:app --reload

# Test in another terminal
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I create an irresistible offer?"}'
```

## 💰 Cost Estimation

### OpenAI API Costs (Approximate)
- **Embeddings**: ~$0.50-2.00 per book (depending on length)
- **Chat Completions**: ~$0.01-0.05 per query
- **Total Setup**: Usually under $5 for 2-3 books

### Example for $100M Offers + $100M Leads:
- **Processing**: ~$2.50 in embedding costs
- **Monthly Usage**: $5-20 depending on query volume
- **Free Tier**: Railway/Vercel hosting remains free

## 🛠️ Troubleshooting

### Common Issues

#### "No book files found"
```bash
# Check your file placement
ls -la backend/data/raw/
# Should show your PDF/EPUB files
```

#### "OpenAI API key not found"
```bash
# Verify your API key is set
echo $OPENAI_API_KEY
# Should display your key (starts with sk-)
```

#### "Permission denied" errors
```bash
# Fix file permissions
chmod +x scripts/*.py
chmod -R 755 backend/data/
```

#### "Module not found" errors
```bash
# Install missing dependencies
pip install -r scripts/requirements.txt
pip install -r backend/requirements.txt
```

### Performance Issues

#### Slow processing
- Use smaller chunk sizes (500-800 words)
- Process books one at a time
- Use sentence_transformer model for faster embeddings

#### Large memory usage
- Reduce batch sizes in the scripts
- Process books individually
- Use cloud processing for large collections

## 📈 Advanced Configuration

### Custom Chunking Strategy
```python
# In scripts/data_processing.py
processor = BookProcessor(
    chunk_size=800,        # Smaller chunks for better precision
    chunk_overlap=150      # Less overlap for more unique content
)
```

### Alternative Embedding Models
```bash
# Use free sentence transformers (no API key needed)
python scripts/run_pipeline.py \
  --books_dir backend/data/raw \
  --output_dir backend/data/chroma \
  --embedding_model sentence_transformer
```

### Multiple Collections
```bash
# Create separate collections for different topics
python scripts/create_embeddings.py \
  --collection_name "offers_knowledge" \
  --input_file backend/data/processed/100m_offers_chunks.json
```

## 🔒 Legal & Ethical Notes

### Important Guidelines
- **Only use books you own**: Purchase books legally
- **Personal use only**: Don't redistribute the processed knowledge
- **Respect copyright**: This is for educational/personal business use
- **Attribution**: The AI will cite sources properly

### Recommended Approach
1. Buy books from official sources
2. Use for personal business development
3. Don't share the trained model
4. Respect Alex Hormozi's intellectual property

## ✅ Verification Checklist

Before deploying, ensure:

- [ ] Books are legally obtained and properly formatted
- [ ] OpenAI API key is working and funded
- [ ] Training pipeline completes without errors
- [ ] Knowledge base contains expected number of chunks
- [ ] Test queries return relevant results
- [ ] Backend API responds correctly
- [ ] Sources are properly attributed

## 🎉 Success!

Once complete, your AI will be able to:
- Answer questions about Alex Hormozi's business strategies
- Provide source citations for all responses
- Search through the complete knowledge base
- Give actionable, framework-based advice

The knowledge base will persist across deployments and can be easily updated with new books or content.

---
*Ready to build your business with AI-powered Hormozi wisdom! 🚀*

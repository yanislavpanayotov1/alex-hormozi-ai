# Hormozi AI Business Advisor

A RAG-based AI assistant trained on Alex Hormozi's business books to provide personalized business advice and insights.

## 🚀 Features

- **Intelligent Q&A**: Ask questions about business strategies, sales, marketing, and operations
- **Source Citations**: Every response includes references to specific book sections
- **Topic Filtering**: Focus on specific business areas (sales, marketing, operations, etc.)
- **Business Calculators**: Interactive tools based on Hormozi's frameworks
- **Case Study Mode**: Apply concepts to your specific business situation

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI Ada-002
- **LLM**: OpenAI GPT-4
- **Language**: Python 3.9+

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context/Hooks
- **Build Tool**: Vite

## 📚 Data Sources

This AI is trained on Alex Hormozi's business books:
- $100M Offers
- $100M Leads
- And other publicly available content

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API Key
- Alex Hormozi's books (PDF/EPUB)

### Quick Setup
1. **Train the Knowledge Base** (REQUIRED):
   ```bash
   # Place books in backend/data/raw/
   export OPENAI_API_KEY="your_key_here"
   python scripts/run_pipeline.py --books_dir backend/data/raw --output_dir backend/data/chroma
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

### 🚀 Deploy for FREE
See `QUICK_DEPLOY.md` for Railway + Vercel deployment (free tiers).

## 📖 Usage

1. Start the backend server
2. Launch the frontend application
3. Ask business questions like:
   - "How do I create irresistible offers?"
   - "What's the best way to generate leads?"
   - "How should I price my services?"

## 🔒 Legal & Ethical

- This tool is for educational purposes
- All content is properly attributed to Alex Hormozi
- AI-generated advice should be considered as guidance, not professional consultation
- Users should verify information and consult professionals for important decisions

## 📈 Development Status

- [x] Project Setup
- [x] Data Processing Pipeline
- [x] Vector Database Implementation  
- [x] RAG System Development
- [x] API Development
- [x] Frontend Interface
- [x] Knowledge Base Training
- [x] Production Deployment Ready
- [ ] Advanced Features (calculators, case studies)

## 🤝 Contributing

This is a personal learning project. Please respect copyright and use responsibly.

## 📄 License

This project is for educational purposes only. All book content rights belong to Alex Hormozi.


# 🚀 Quick Deploy Reference

## 0️⃣ Train Knowledge Base (REQUIRED FIRST!)
```bash
# 1. Place Alex Hormozi books in backend/data/raw/
# 2. Set OpenAI API key
export OPENAI_API_KEY="your_key_here"

# 3. Train the AI (10-20 minutes)
python scripts/run_pipeline.py \
  --books_dir backend/data/raw \
  --output_dir backend/data/chroma \
  --embedding_model openai

# 4. Test it works
python test_knowledge_base.py
```

## 1️⃣ Push to GitHub
```bash
git add .
git commit -m "Add trained knowledge base"
git push origin main
```

## 2️⃣ Railway (Backend) - FREE
1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. **Root Directory**: `backend`
4. **Environment Variables**:
   ```
   OPENAI_API_KEY=your_openai_api_key
   CHROMA_PERSIST_DIRECTORY=/app/data/chroma
   DEBUG=False
   ENVIRONMENT=production
   ```
5. Copy your Railway URL: `https://xxx.up.railway.app`

## 3️⃣ Vercel (Frontend) - FREE
1. Go to [vercel.com](https://vercel.com)
2. "New Project" → Import GitHub repo
3. **Root Directory**: `frontend`
4. **Environment Variable**:
   ```
   VITE_API_URL=https://your-railway-url.up.railway.app
   ```
5. Deploy!

## 4️⃣ Update Backend CORS
1. Copy Vercel URL: `https://your-app.vercel.app`
2. Add to Railway environment variables:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ```

## ✅ Done!
- **Cost**: $0 (free tiers)
- **Backend**: Railway
- **Frontend**: Vercel
- **Limits**: 500h/month Railway, unlimited Vercel

---
*See `DEPLOYMENT_GUIDE.md` for detailed instructions*

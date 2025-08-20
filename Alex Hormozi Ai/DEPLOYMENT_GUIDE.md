# 🚀 Free Deployment Guide: Railway + Vercel

This guide will help you deploy your Hormozi AI application for **FREE** using Railway (backend) and Vercel (frontend).

## 📋 Prerequisites

- GitHub account
- Railway account (free tier: 500 hours/month)
- Vercel account (free tier: unlimited for personal projects)
- **OpenAI API key** (for embeddings and chat)
- **Alex Hormozi's books** (PDF/EPUB format)
- Python 3.9+ (for knowledge training)

## 🧠 Part 1: Train the Knowledge Base (REQUIRED)

**⚠️ IMPORTANT: You must train the AI with Alex Hormozi's knowledge before deployment!**

### Step 1: Set Up Books and Environment
1. **Get Alex Hormozi's books** (PDF/EPUB format):
   - $100M Offers
   - $100M Leads
   - Place them in `backend/data/raw/`

2. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

3. **Install dependencies**:
   ```bash
   pip install -r scripts/requirements.txt
   ```

### Step 2: Run the Training Pipeline
```bash
# Train the knowledge base (takes 10-20 minutes)
python scripts/run_pipeline.py \
  --books_dir backend/data/raw \
  --output_dir backend/data/chroma \
  --embedding_model openai
```

### Step 3: Test Your Knowledge Base
```bash
# Verify everything works
python test_knowledge_base.py
```

**✅ Once training is complete, you'll have a `backend/data/chroma/` directory with your trained knowledge base.**

## 🛤️ Part 2: Deploy Backend on Railway

### Step 1: Prepare Your Repository
1. **Commit your trained knowledge base**:
   ```bash
   git add .
   git commit -m "Add trained Hormozi knowledge base"
   git push origin main
   ```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the backend folder and Dockerfile
5. Set the **Root Directory** to `backend`

### Step 3: Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:
```
OPENAI_API_KEY=your_actual_openai_api_key
CHROMA_PERSIST_DIRECTORY=/app/data/chroma
DEBUG=False
ENVIRONMENT=production
```

### Step 4: Get Your Railway URL
- After deployment, Railway will provide you with a URL like: `https://your-app-name.up.railway.app`
- Copy this URL - you'll need it for the frontend configuration

## 🌐 Part 3: Deploy Frontend on Vercel

### Step 1: Configure Environment Variables
1. Create a `.env.local` file in your frontend directory:
   ```bash
   cd frontend
   echo "VITE_API_URL=https://your-railway-url.up.railway.app" > .env.local
   ```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click "New Project" → Import your GitHub repository
3. Set the **Root Directory** to `frontend`
4. Add environment variable:
   - Key: `VITE_API_URL`
   - Value: `https://your-railway-url.up.railway.app` (from Railway)
5. Click "Deploy"

## Part 4: Update Backend CORS

### Step 1: Update Backend CORS
1. After Vercel deployment, copy your Vercel URL (e.g., `https://your-app.vercel.app`)
2. Go back to Railway → Variables and add:
   ```
   FRONTEND_URL=https://your-app.vercel.app
   ```
3. Railway will automatically redeploy with the new CORS settings

## 🎯 Part 3: Verification

### Test Your Deployment
1. Visit your Vercel URL
2. Try sending a test message
3. Check that the backend responds correctly

### Health Checks
- Backend health: `https://your-railway-url.up.railway.app/health`
- Frontend: Your Vercel URL should load the React app

## 💰 Free Tier Limits

### Railway (Free Tier)
- 500 execution hours per month
- 1GB RAM
- 1GB disk
- No credit card required

### Vercel (Free Tier)
- Unlimited deployments
- 100GB bandwidth per month
- No credit card required for personal projects

## 🔧 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Make sure `FRONTEND_URL` is set correctly in Railway
   - Check that your Vercel URL is added to CORS origins

2. **Railway Build Fails**
   - Ensure the Root Directory is set to `backend`
   - Check that all required environment variables are set

3. **Vercel Build Fails**
   - Ensure the Root Directory is set to `frontend`
   - Check that `VITE_API_URL` environment variable is set

4. **API Connection Issues**
   - Verify the Railway URL is accessible
   - Check that the backend is running (visit `/health` endpoint)

### Support Commands

```bash
# Check Railway logs
railway logs

# Test API locally
curl https://your-railway-url.up.railway.app/health

# Test frontend build locally
cd frontend
npm run build
npm run preview
```

## 🎉 Success!

Your Hormozi AI application is now deployed and running for free! 

- **Backend**: Railway handles your FastAPI server
- **Frontend**: Vercel serves your React application
- **Database**: ChromaDB data persists on Railway's disk
- **Cost**: $0 (within free tier limits)

## 📈 Next Steps

1. Set up custom domains (optional)
2. Add monitoring and analytics
3. Implement the full RAG system
4. Add user authentication
5. Scale as needed with paid tiers

---
*Happy deploying! 🚀*

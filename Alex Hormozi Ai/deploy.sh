#!/bin/bash

# Deployment script for Hormozi AI
echo "🚀 Preparing Hormozi AI for deployment..."

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Install Vercel CLI if not present
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

echo "✅ Prerequisites installed!"
echo ""
echo "🛤️  Next steps:"
echo "1. Push your code to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for deployment'"
echo "   git push origin main"
echo ""
echo "2. Deploy backend on Railway:"
echo "   - Visit https://railway.app"
echo "   - Create new project from GitHub repo"
echo "   - Set root directory to 'backend'"
echo "   - Add environment variables (see DEPLOYMENT_GUIDE.md)"
echo ""
echo "3. Deploy frontend on Vercel:"
echo "   - Visit https://vercel.com"
echo "   - Import GitHub repository"
echo "   - Set root directory to 'frontend'"
echo "   - Add VITE_API_URL environment variable"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"

#!/bin/bash

# Hormozi AI Business Advisor Setup Script
# This script sets up the development environment for the Hormozi AI project

set -e

echo "🚀 Setting up Hormozi AI Business Advisor..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.9+
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
}

# Check if Node.js 18+ is installed
check_node() {
    print_status "Checking Node.js installation..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js $NODE_VERSION found"
        
        # Check if version is 18+
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [ "$NODE_MAJOR" -ge 18 ]; then
            print_success "Node.js version is compatible"
        else
            print_error "Node.js 18+ is required. Found: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
}

# Setup Python virtual environment and install dependencies
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp .env.example .env
        print_warning "Please edit backend/.env and add your OpenAI API key"
    fi
    
    print_success "Backend setup complete"
    cd ..
}

# Setup frontend dependencies
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend
    
    # Install npm dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating frontend .env file..."
        echo "VITE_API_URL=http://localhost:8000" > .env
    fi
    
    print_success "Frontend setup complete"
    cd ..
}

# Setup scripts dependencies
setup_scripts() {
    print_status "Setting up data processing scripts..."
    
    cd scripts
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating scripts virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing script dependencies..."
    pip install -r requirements.txt
    
    print_success "Scripts setup complete"
    cd ..
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/data/raw
    mkdir -p backend/data/processed  
    mkdir -p backend/data/embeddings
    mkdir -p backend/data/chroma
    
    print_success "Directories created"
}

# Main setup function
main() {
    echo "=================================================="
    echo "🧠 Hormozi AI Business Advisor Setup"
    echo "=================================================="
    
    check_python
    check_node
    create_directories
    setup_backend
    setup_frontend
    setup_scripts
    
    echo ""
    echo "=================================================="
    print_success "Setup completed successfully! 🎉"
    echo "=================================================="
    echo ""
    echo "Next steps:"
    echo "1. Add your OpenAI API key to backend/.env"
    echo "2. Place Alex Hormozi's books (PDF/EPUB) in backend/data/raw/"
    echo "3. Process the books:"
    echo "   cd scripts && source venv/bin/activate"
    echo "   python data_processing.py --input_dir ../backend/data/raw --output_dir ../backend/data/processed"
    echo "   python create_embeddings.py --input_file ../backend/data/processed/processed_chunks.json --output_dir ../backend/data/chroma"
    echo ""
    echo "4. Start the backend:"
    echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
    echo "5. Start the frontend (in a new terminal):"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "6. Open http://localhost:3000 in your browser"
    echo ""
    print_warning "Remember: This tool is for educational purposes only."
    print_warning "Always respect copyright and use responsibly."
}

# Run main function
main


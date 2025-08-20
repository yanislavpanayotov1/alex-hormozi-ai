FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend application
COPY backend/ .

# Copy the Gradio frontend
COPY app.py .

# Create data directories and copy trained knowledge base
RUN mkdir -p data/raw data/processed data/embeddings
COPY backend/data/ ./data/

# Expose ports (7860 for Gradio, 8000 for API)
EXPOSE 7860
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 &\n\
python app.py' > /app/start.sh && chmod +x /app/start.sh

# Command to run both API and Gradio interface
CMD ["/app/start.sh"]

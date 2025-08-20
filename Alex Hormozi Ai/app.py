"""
Simple Gradio interface for Alex Hormozi AI
This provides a web UI that works well with Hugging Face Spaces
"""

import gradio as gr
import requests
import json
import os

# API endpoint (will be localhost in Hugging Face Spaces)
API_URL = "http://localhost:8000"

def query_hormozi_ai(question, api_key):
    """Query the Hormozi AI backend"""
    if not question.strip():
        return "Please ask a question about business, offers, or lead generation.", ""
    
    if not api_key.strip():
        return "Please provide your OpenAI API key to get responses.", ""
    
    try:
        # Set the API key as environment variable for the backend
        headers = {"Content-Type": "application/json"}
        payload = {
            "message": question,
            "conversation_id": None
        }
        
        # Add API key to environment (backend will pick it up)
        os.environ["OPENAI_API_KEY"] = api_key
        
        response = requests.post(f"{API_URL}/chat", json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "No response received")
            sources = data.get("sources", [])
            
            # Format sources
            sources_text = ""
            if sources:
                sources_text = "\n\n**Sources:**\n"
                for i, source in enumerate(sources, 1):
                    book = source.get("book", "Unknown")
                    chapter = source.get("chapter", "Unknown") 
                    snippet = source.get("text_snippet", "")[:200]
                    sources_text += f"{i}. **{book}** - {chapter}\n   _{snippet}_...\n\n"
            
            return answer, sources_text
        else:
            return f"Error: {response.status_code} - {response.text}", ""
            
    except requests.exceptions.RequestException as e:
        return f"Connection error: {str(e)}", ""
    except Exception as e:
        return f"Error: {str(e)}", ""

def check_api_status():
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return "✅ API is running"
        else:
            return f"❌ API error: {response.status_code}"
    except:
        return "❌ API is not responding"

# Create Gradio interface
with gr.Blocks(title="Alex Hormozi AI Business Advisor", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1>💼 Alex Hormozi AI Business Advisor</h1>
        <p>Get business advice based on Alex Hormozi's proven strategies from $100M Offers, $100M Leads, and Lost Chapters</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column():
            api_key = gr.Textbox(
                label="OpenAI API Key",
                placeholder="sk-...",
                type="password",
                info="Your OpenAI API key (required for responses)"
            )
            
            question = gr.Textbox(
                label="Ask Alex Hormozi AI",
                placeholder="How do I create an irresistible offer?",
                lines=3
            )
            
            submit_btn = gr.Button("Get Business Advice", variant="primary")
            
        with gr.Column():
            status = gr.Textbox(label="API Status", value=check_api_status())
            
    with gr.Row():
        with gr.Column():
            answer = gr.Textbox(
                label="Answer",
                lines=10,
                max_lines=20
            )
            
        with gr.Column():
            sources = gr.Textbox(
                label="Sources",
                lines=10,
                max_lines=20
            )
    
    gr.HTML("""
    <div style="text-align: center; padding: 20px; margin-top: 20px; border-top: 1px solid #ddd;">
        <h3>💡 Example Questions</h3>
        <p><strong>Offers:</strong> "How do I create an irresistible offer?" • "What makes an offer compelling?"</p>
        <p><strong>Leads:</strong> "What's the best way to generate leads?" • "How do I improve my lead quality?"</p>
        <p><strong>Business:</strong> "How should I price my services?" • "What's the key to scaling a business?"</p>
        <p><strong>Sales:</strong> "How do I increase my close rate?" • "What's the best sales framework?"</p>
    </div>
    """)
    
    # Event handlers
    submit_btn.click(
        fn=query_hormozi_ai,
        inputs=[question, api_key],
        outputs=[answer, sources]
    )
    
    question.submit(
        fn=query_hormozi_ai,
        inputs=[question, api_key],
        outputs=[answer, sources]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)

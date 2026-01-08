# Source Code Directory

## Purpose
Contains the core Python backend application code for PCBot.

## Contents

### Main Applications
- **`app.py`**: Streamlit-based interface (legacy)
- **`widget_api.py`**: Flask REST API server for widget interface (current production)
- **`rag_langchain.py`**: RAG pipeline implementation using LangChain

### Modules
- **`models/`**: LLM model configurations (Ollama, Groq, Qwen)
- **`utils/`**: Utility functions (persistence, text processing)
- **`assets/`**: Static assets (images, icons)
- **`data/`**: Data files and configurations

## Usage

### Start Flask API Server
```bash
python widget_api.py
```

### Start Streamlit App (Legacy)
```bash
streamlit run app.py
```

## Key Features
- RESTful API endpoints for chat functionality
- RAG pipeline with Qdrant vector database
- Multi-model LLM support (Ollama Mistral, Groq)
- Session management and authentication
- Admin endpoints for statistics and calibration

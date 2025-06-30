# RAG Application Docker Setup

This is a RAG (Retrieval-Augmented Generation) application that scrapes a website, creates embeddings, and provides question-answering capabilities using OpenAI's API.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Quick Start

1. **Set up environment variables:**
   Create a `.env` file in the project root with your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - API documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Alternative: Build and run manually

1. **Build the Docker image:**
   ```bash
   docker build -t rag-app .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 --env-file .env rag-app
   ```

## API Usage

Send POST requests to `/ask` endpoint with a JSON body:
```json
{
  "query": "Your question here"
}
```

## Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `EMBED_MODEL` (optional): Embedding model (default: text-embedding-3-small)
- `CHAT_MODEL` (optional): Chat model (default: gpt-4)
- `TARGET_URL` (optional): Website to scrape (default: https://woocommercegst.co.in/)

## Features

- Web scraping with BeautifulSoup
- Text chunking and embedding generation
- Vector search with FAISS
- Question answering with context
- FastAPI REST API
- CORS enabled
- Health checks
- Non-root user for security

## Troubleshooting

- Make sure your OpenAI API key is valid and has sufficient credits
- Check the logs: `docker-compose logs rag-app`
- The application will scrape the target website on startup, which may take a few moments 
# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core import scrape_site, chunk_text, build_vector_store, get_relevant_chunks, chat_with_context
from app.config import TARGET_URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache chunks and vector index at startup
print("🔄 Scraping and preparing vector store...")
raw_text = scrape_site(TARGET_URL)
chunks = chunk_text(raw_text)
vector_index, chunk_store = build_vector_store(chunks)
print("✅ Vector store ready!")

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    query = data.get("query", "")

    relevant_chunks = get_relevant_chunks(query, vector_index, chunk_store)
    answer = chat_with_context(query, relevant_chunks)

    return {"answer": answer}

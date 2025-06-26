# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core import scrape_site, chunk_text, build_vector_store, get_relevant_chunks, chat_with_context
from app.config import TARGET_URL
import random

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
    query = data.get("query", "").strip().lower()

    # Fallback for small/generic queries
    fallback_queries = {
        "hi", "hello", "ok", "okay", "hey", "thanks", "thank you", "yo", "sup", "hola", "hii", "hiii", "test",
        "yo!", "hey!", "hi!", "hello!", "ok!", "okay!", "sup?", "hey there", "greetings", "good morning", "good evening", "good afternoon",
        "nice", 'heyy',"cool", "fine", "awesome", "great", "good", "hru", "how are you", "what's up", "wassup", "yo yo", "hlo", "hlo!", "hlo there"
    }
    fallback_responses = [
        "Hello! How can I help you today?",
        "Hi there! What can I do for you?",
        "Hey! How may I assist you?",
        "Greetings! How can I help?",
        "Hello! Need any assistance?",
        "Hi! How can I support you today?",
        "Hey there! What brings you here today?",
        "Hi! Let me know if you have any questions.",
        "Hello! I'm here to help."
    ]
    if query in fallback_queries or len(query) <= 3:
        return {"answer": random.choice(fallback_responses)}

    relevant_chunks = get_relevant_chunks(query, vector_index, chunk_store)
    answer = chat_with_context(query, relevant_chunks)

    return {"answer": answer}

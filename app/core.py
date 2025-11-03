# app/core.py

import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss
import json
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from app.config import OPENAI_API_KEY, TARGET_URL, CHAT_MODEL, HELICONE_API_KEY

# 🔹 GPT Client (for answering)
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://oai.helicone.ai/v1",
    default_headers={"Helicone-Auth": f"Bearer sk-helicone-wvtrzoy-2v5esza-qhp3lky-v5ipnhy" }
)

# 🔹 Local embedding model (fast + free)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Scrape site HTML and extract text
def scrape_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = [tag.get_text(strip=True) for tag in soup.find_all(
        ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
         'li', 'strong', 'span', 'div', 'a', 'em', 'b', 'blockquote'])]
    return "\n".join(texts)


# ✅ Chunk plain scraped text
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# ✅ Generate embedding using local transformer
def get_embedding(text):
    return embedding_model.encode([text])[0]

# ✅ Build FAISS index from chunk embeddings
def build_vector_store(chunks):
    embeddings = embedding_model.encode(chunks, batch_size=32, show_progress_bar=True)
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index, chunks

# ✅ Retrieve top-k most relevant chunks
def get_relevant_chunks(query, index, chunks, top_k=3):
    query_embedding = np.array(get_embedding(query)).astype("float32").reshape(1, -1)
    D, I = index.search(query_embedding, top_k)
    return [chunks[i] for i in I[0]]

# ✅ Use GPT-4 to answer based on relevant chunks
def chat_with_context(query, relevant_chunks):
    prompt = (
         "You're an expert on GST Invoice Plugin for WooCommerce and their settings here is their website https://gstforecom.com . Use the provided info below if it's relevant chunks. "
        "If the answer isn't found, do your best to help using your general knowledge.\n\n"
        f"Info:\n{''.join(relevant_chunks)}\n\nQ: {query}"
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

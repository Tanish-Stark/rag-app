# app/core.py

import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss
from openai import OpenAI
from app.config import OPENAI_API_KEY, TARGET_URL, EMBED_MODEL, CHAT_MODEL


client = OpenAI(api_key=OPENAI_API_KEY)

def scrape_site(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    texts = [tag.get_text(strip=True) for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
'li', 'strong', 'span', 'div', 'a', 'em', 'b', 'blockquote'])]
    return "\n".join(texts)

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def get_embedding(text):
    response = client.embeddings.create(input=[text], model=EMBED_MODEL)
    return response.data[0].embedding

def build_vector_store(chunks):
    embeddings = [get_embedding(chunk) for chunk in chunks]
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype("float32"))
    return index, chunks

def get_relevant_chunks(query, index, chunks, top_k=3):
    query_embedding = np.array(get_embedding(query)).astype("float32").reshape(1, -1)
    D, I = index.search(query_embedding, top_k)
    return [chunks[i] for i in I[0]]

def chat_with_context(query, relevant_chunks):
    prompt = (
        "Answer the following question. If the provided info contains the answer, use it. "
        "If the info is insufficient, answer based on your general knowledge.\n\n"
        f"Info:\n{''.join(relevant_chunks)}\n\nQ: {query}"
    )
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

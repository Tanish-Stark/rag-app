# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core import scrape_site, chunk_text, build_vector_store, get_relevant_chunks, chat_with_context
from app.config import TARGET_URL
import random
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache chunks and vector index at startup
print("🔄 Scraping and preparing vector store...")
with open("raw_text.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()
chunks = chunk_text(raw_text)
print(f"🔹 Scraped chunks: {len(chunks)}")


vector_index, chunk_store = build_vector_store(chunks)
print("✅ Vector store ready!")

def categorize_query(query):
    """Categorize the query into different types for appropriate fallback responses."""
    query_lower = query.lower().strip()
    
    # Pricing-related queries (refined to only match direct price/cost queries)
    pricing_patterns = [
        r'\b(price|cost|fee|rate|charges?)\b',
        r'how much( does it)? (cost|is it|do i pay|to buy|to purchase)',
        r'what( is|\'s)? the (price|cost|fee|rate)',
        r'price of( the)? (pro|premium)? ?plan',
        r'cost of( the)? (pro|premium)? ?plan',
        r'how much for( the)? (pro|premium)? ?plan',
        r'how much do(es)? (the )?(pro|premium)? ?plan cost',
    ]
    for pattern in pricing_patterns:
        if re.search(pattern, query_lower):
            return "pricing"
    
    # Thanks and gratitude expressions
    thanks_patterns = [
        r'\b(thanks?|thank\s+you|thx|ty|tnx|thnx)\b',
        r'\b(grateful|appreciate|appreciated)\b',
        r'\b(thanks\s+a\s+lot|thanks\s+so\s+much|thank\s+you\s+so\s+much)\b'
    ]
    
    # Greetings
    greeting_patterns = [
        r'\b(hi|hello|hey|hola|hii+|yo|sup|wassup|hlo|greetings)\b',
        r'\b(good\s+(morning|afternoon|evening|night))\b',
        r'\b(how\s+are\s+you|hru|how\s+you\s+doing)\b'
    ]
    
    # Affirmative responses
    affirmative_patterns = [
        r'\b(ok|okay|sure|yes|yeah|yep|yup|fine|good|great|awesome|cool|nice)\b',
        r'\b(alright|all\s+right|got\s+it|understood)\b'
    ]
    
    # Negative responses
    negative_patterns = [
        r'\b(no|nope|nah|not\s+really|not\s+sure|dont\s+know|don\'t\s+know)\b'
    ]
    
    # Test queries
    test_patterns = [
        r'\b(test|testing|ping|pong)\b'
    ]
    
    # Creator-related queries
    creator_patterns = [
        r'who (is|\'s)? (the )?(creator|author|developer|builder|maker|founder) (of (this )?(plugin|app|application|software|project|tool)|of gstforecom|gstforecom)?\??',
        r'who (made|built|created|developed) (this )?(plugin|app|application|software|project|tool|gstforecom)\??',
        r'who is behind (this )?(plugin|app|application|software|project|tool|gstforecom)\??',
        r'creator of (this )?(plugin|app|application|software|project|tool|gstforecom)\??',
        r'author of (this )?(plugin|app|application|software|project|tool|gstforecom)\??',
        r'developer of (this )?(plugin|app|application|software|project|tool|gstforecom)\??',
    ]
    
    # Check patterns
    for pattern in thanks_patterns:
        if re.search(pattern, query_lower):
            return "thanks"
    
    for pattern in greeting_patterns:
        if re.search(pattern, query_lower):
            return "greeting"
    
    for pattern in affirmative_patterns:
        if re.search(pattern, query_lower):
            return "affirmative"
    
    for pattern in negative_patterns:
        if re.search(pattern, query_lower):
            return "negative"
    
    for pattern in test_patterns:
        if re.search(pattern, query_lower):
            return "test"
    
    for pattern in creator_patterns:
        if re.search(pattern, query_lower):
            return "creator"
    
    # Very short queries (1-3 characters)
    if len(query_lower) <= 3:
        return "short"
    
    return None

def get_fallback_response(query_type):
    """Get appropriate fallback response based on query type."""
    
    responses = {
        "pricing": [
            "We offer two plans: The Free plan is free forever, and the Pro plan is ₹4999. Let me know if you need more details!",
            "Our pricing options: Free plan (free forever) and Pro plan (₹4999). Feel free to ask about features or upgrades!",
            "You can use the Free plan at no cost, or upgrade to the Pro plan for ₹4999. Let me know if you want to know more!"
        ],
        "thanks": [
            "You're welcome! I'm glad I could help.",
            "You're very welcome! Feel free to ask if you need anything else.",
            "My pleasure! Let me know if you have more questions.",
            "You're welcome! Happy to assist you.",
            "No problem at all! I'm here to help whenever you need.",
            "You're welcome! Don't hesitate to reach out if you need further assistance.",
            "Glad I could help! Feel free to ask more questions anytime."
        ],
        "greeting": [
            "Hello! How can I help you today?",
            "Hi there! What can I do for you?",
            "Hey! How may I assist you?",
            "Greetings! How can I help?",
            "Hello! Need any assistance?",
            "Hi! How can I support you today?",
            "Hey there! What brings you here today?",
            "Hi! Let me know if you have any questions.",
            "Hello! I'm here to help."
        ],
        "affirmative": [
            "Great! What would you like to know?",
            "Perfect! How can I assist you?",
            "Excellent! What can I help you with?",
            "Good! What questions do you have?",
            "Awesome! What would you like to learn about?",
            "Cool! How can I be of service?"
        ],
        "negative": [
            "No worries! Let me know if you change your mind.",
            "That's okay! Feel free to ask if you need help later.",
            "No problem! I'm here when you're ready.",
            "Alright! Just let me know if you have any questions."
        ],
        "test": [
            "Hello! I'm working fine. How can I help you?",
            "Hi! The system is running smoothly. What can I do for you?",
            "Hello! Everything is operational. How may I assist you?"
        ],
        "short": [
            "Hi! Could you please provide more details about what you're looking for?",
            "Hello! I'd be happy to help, but I need a bit more information.",
            "Hi there! What would you like to know more about?"
        ],
        "creator": [
            "GST Invoice Plugin for WooCommerce is created by STARK DIGITAL INDIA. Learn more at https://www.starkdigital.net/",
            "The creator of GST Invoice Plugin for WooCommerce is STARK DIGITAL INDIA. Visit https://www.starkdigital.net/ for more info.",
            "GST Invoice Plugin for WooCommerce was developed by STARK DIGITAL INDIA. Check out their website: https://www.starkdigital.net/"
        ]
    }
    
    return random.choice(responses.get(query_type, responses["greeting"]))

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    query = data.get("query", "").strip()


    # Categorize the query
    query_type = categorize_query(query)
    
    # If it's a fallback type, return appropriate response
    if query_type:
        return {"answer": get_fallback_response(query_type)}

    # Otherwise, process with the RAG system
    relevant_chunks = get_relevant_chunks(query, vector_index, chunk_store)
    answer = chat_with_context(query, relevant_chunks)

    return {"answer": answer}

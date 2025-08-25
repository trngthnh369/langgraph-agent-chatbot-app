import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os
import numpy as np
import chromadb
import json

chroma_client = chromadb.PersistentClient("db")
collection_name = 'products'

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def get_embedding(text: str) -> list[float]:
    """Generate embeddings using Gemini API"""
    try:
        # Use Gemini's embedding model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return result['embedding']
    except Exception as e:
        print(f"Error generating embedding: {e}")
        # Fallback to a simple hash-based embedding (not recommended for production)
        import hashlib
        hash_object = hashlib.md5(text.encode())
        # Convert to a simple numeric representation
        return [float(ord(c)) for c in hash_object.hexdigest()[:100]]

def rag(query: str) -> str:
    """Retrieve relevant product information using RAG"""
    try:
        collection = chroma_client.get_collection(name=collection_name)
        query_embedding = get_embedding(query)
        
        # Normalize the embedding
        query_embedding = np.array(query_embedding)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Perform vector search
        search_results = collection.query(
            query_embeddings=query_embedding.tolist(), 
            n_results=5  # Increased for better context
        )

        metadatas = search_results.get('metadatas', [])
        search_result = ""
        
        for i, metadata_list in enumerate(metadatas):
            if isinstance(metadata_list, list):
                for j, metadata in enumerate(metadata_list):
                    if isinstance(metadata, dict):
                        combined_text = metadata.get('information', 'No text available').strip()
                        search_result += f"{i + 1}). {combined_text}\n\n"
        
        return search_result if search_result else "No relevant product information found."
        
    except Exception as e:
        print(f"Error in RAG: {e}")
        return "Unable to retrieve product information at the moment."

def shop_information_rag():
    """Return shop information"""
    return [
        {
            "address": "89 Đ. Tam Trinh, Mai Động, Hoàng Mai, Hà Nội 100000, Vietnam",
            "maps_url": "https://maps.app.goo.gl/SitTbiYwUpu8jpeRA",
            "opening_hours": "8:30 AM–9:30 PM",
            "phone": "+84 24 1234 5678",
            "services": ["Product consultation", "Warranty support", "Technical support"]
        },
        {
            "address": "27A Nguyễn Công Trứ, Phạm Đình Hổ, Hai Bà Trưng, Hà Nội 100000, Vietnam",
            "maps_url": "https://maps.app.goo.gl/3L7iSHpbHawsEaTx9",
            "opening_hours": "8:30 AM–9:30 PM",
            "phone": "+84 24 1234 5679",
            "services": ["Product consultation", "Warranty support", "Repair services"]
        },
        {
            "address": "392 Đ. Trương Định, Tương Mai, Hoàng Mai, Hà Nội, Vietnam",
            "maps_url": "https://maps.app.goo.gl/torAE2bHddW6nMPq9",
            "opening_hours": "8:30 AM–9:30 PM",
            "phone": "+84 24 1234 5680",
            "services": ["Product consultation", "Express delivery", "Installation support"]
        }
    ]

def search_internet(query: str) -> str:
    """Search the internet using SerpAPI"""
    try:
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        
        if not serpapi_key:
            return "Internet search is not available. Please configure SERPAPI_API_KEY."
        
        # SerpAPI endpoint
        url = "https://serpapi.com/search"
        
        params = {
            "q": query,
            "api_key": serpapi_key,
            "engine": "google",
            "num": 5,  # Number of results
            "hl": "vi",  # Language
            "gl": "vn"   # Country
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            search_results = ""
            organic_results = data.get('organic_results', [])
            
            for i, result in enumerate(organic_results[:3]):  # Top 3 results
                title = result.get('title', 'No title')
                snippet = result.get('snippet', 'No description')
                link = result.get('link', '')
                
                search_results += f"{i + 1}. {title}\n"
                search_results += f"   {snippet}\n"
                search_results += f"   Source: {link}\n\n"
            
            # Also include answer box if available
            answer_box = data.get('answer_box', {})
            if answer_box:
                answer = answer_box.get('answer', '')
                if answer:
                    search_results = f"Quick Answer: {answer}\n\n" + search_results
            
            return search_results if search_results else "No relevant information found on the internet."
            
        else:
            return f"Internet search failed with status code: {response.status_code}"
            
    except Exception as e:
        print(f"Error in internet search: {e}")
        return "Unable to perform internet search at the moment."

def rag_with_fallback(query: str, search_type: str = "product") -> str:
    """Enhanced RAG with internet search fallback"""
    try:
        if search_type == "product":
            # Try product RAG first
            rag_result = rag(query)
            
            # If RAG doesn't return good results, try internet search
            if "No relevant" in rag_result or len(rag_result.strip()) < 50:
                print("[System] RAG results insufficient, trying internet search...")
                internet_result = search_internet(f"{query} site:hoanghamobile.com OR smartphone OR mobile phone")
                return f"Database Results:\n{rag_result}\n\nInternet Search Results:\n{internet_result}"
            else:
                return rag_result
                
        elif search_type == "shop":
            # For shop information, combine local data with internet search
            local_info = shop_information_rag()
            local_info_text = "\n".join([
                f"Store {i+1}: {shop['address']}, Hours: {shop['opening_hours']}, Phone: {shop['phone']}"
                for i, shop in enumerate(local_info)
            ])
            
            # Add internet search for additional shop information
            internet_result = search_internet(f"{query} HoangHaMobile store Vietnam")
            
            return f"Store Information:\n{local_info_text}\n\nAdditional Information:\n{internet_result}"
            
        else:
            # General search
            return search_internet(query)
            
    except Exception as e:
        print(f"Error in enhanced RAG: {e}")
        return "Unable to retrieve information at the moment."
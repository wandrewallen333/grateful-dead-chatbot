from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timedelta

# Import your existing chatbot classes
import json
from typing import List, Dict, Any
import requests
from sentence_transformers import SentenceTransformer
import chromadb
import openai
import re
from bs4 import BeautifulSoup

load_dotenv()

class GratefulDeadChatbot:
    def __init__(self, openai_api_key: str):
        """Initialize the Grateful Dead RAG chatbot for API use"""
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize vector database
        self.chroma_client = chromadb.PersistentClient(path="./dead_knowledge_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="grateful_dead_knowledge",
            metadata={"description": "Grateful Dead knowledge base"}
        )
        
        # Initialize session for web requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def add_knowledge_to_db(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector database"""
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            text = doc['content']
            metadata = {k: v for k, v in doc.items() if k != 'content'}
            
            texts.append(text)
            metadatas.append(metadata)
            ids.append(f"doc_{i}_{hash(text) % 100000}")
        
        embeddings = self.embedding_model.encode(texts).tolist()
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )
    
    def search_knowledge(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            relevant_docs = []
            for i in range(len(results['documents'][0])):
                relevant_docs.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return relevant_docs
        except Exception as e:
            print(f"Error searching knowledge base: {e}")
            return []
    
    def generate_response(self, user_query: str, context_docs: List[Dict], conversation_history: List[Dict] = None) -> str:
        """Generate response using OpenAI with retrieved context AND conversation history"""
        
        # Build context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in context_docs])
        
        # Build conversation history
        conversation_context = ""
        if conversation_history:
            # Include last 6 messages for context (3 exchanges)
            recent_history = conversation_history[-6:]
            conversation_context = "\n\nRecent conversation:\n"
            for msg in recent_history:
                role = "Human" if msg['role'] == 'user' else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        system_prompt = """You are the ultimate Grateful Dead expert and enthusiast! You have deep knowledge about:
        - All Grateful Dead songs, albums, and performances
        - Band members past and present (Jerry Garcia, Bob Weir, Phil Lesh, etc.)
        - Tour history, venues, and memorable shows
        - The Dead community and culture
        - Related bands and solo projects
        
        Use the provided context to answer questions accurately. Pay attention to the conversation history to provide relevant follow-up responses.
        If someone asks a follow-up question, refer back to what you discussed earlier.
        Keep the vibe conversational and friendly - like talking to a fellow Deadhead.
        Use Grateful Dead terminology and references naturally when appropriate.
        
        Context information:
        {context}
        {conversation_context}
        """
        
        try:
            # Build message history for OpenAI
            messages = [
                {"role": "system", "content": system_prompt.format(context=context, conversation_context=conversation_context)}
            ]
            
            # Add recent conversation to OpenAI messages
            if conversation_history:
                # Add last 4 messages for better context
                for msg in conversation_history[-4:]:
                    messages.append({"role": msg['role'], "content": msg['content']})
            
            # Add current question
            messages.append({"role": "user", "content": user_query})
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I'm having trouble connecting right now. Error: {str(e)}"
    
    def chat(self, user_input: str, conversation_history: List[Dict] = None) -> str:
        """Main chat method with conversation memory"""
        if not user_input.strip():
            return "What would you like to know about the Grateful Dead?"
        
        relevant_docs = self.search_knowledge(user_input)
        response = self.generate_response(user_input, relevant_docs, conversation_history)
        return response

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dead-heads-unite-' + str(uuid.uuid4()))
CORS(app, supports_credentials=True)

# Store conversations in memory (in production, use Redis or a database)
conversations = {}

# Clean up old conversations periodically
def cleanup_old_conversations():
    """Remove conversations older than 2 hours"""
    cutoff_time = datetime.now() - timedelta(hours=2)
    to_remove = []
    
    for session_id, data in conversations.items():
        if data['last_activity'] < cutoff_time:
            to_remove.append(session_id)
    
    for session_id in to_remove:
        del conversations[session_id]

# Initialize chatbot
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable required")

print("Initializing Grateful Dead Chatbot API...")
chatbot = GratefulDeadChatbot(api_key)

# Initialize knowledge base if needed
try:
    count = chatbot.collection.count()
    if count == 0:
        print("Initializing knowledge base...")
        sample_docs = [
            {
                "content": "Jerry Garcia was the lead guitarist and primary songwriter for the Grateful Dead. Born Jerome John Garcia on August 1, 1942, in San Francisco, he was known for his distinctive guitar playing style and improvisational skills.",
                "category": "band_members",
                "person": "Jerry Garcia",
                "type": "biography"
            },
            {
                "content": "Dark Star is one of the Grateful Dead's most famous and experimental songs. Written by Jerry Garcia and Robert Hunter, it became a vehicle for extended improvisation during live performances.",
                "category": "songs",
                "song": "Dark Star",
                "type": "song_info"
            }
        ]
        chatbot.add_knowledge_to_db(sample_docs)
        print("Knowledge base initialized!")
    else:
        print(f"Knowledge base loaded with {count} documents")
except Exception as e:
    print(f"Warning: Could not initialize knowledge base: {e}")

print("Grateful Dead Chatbot API ready!")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Grateful Dead Chatbot API is running",
        "knowledge_base_size": chatbot.collection.count(),
        "active_conversations": len(conversations)
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with conversation memory"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' in request body"
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message.strip():
            return jsonify({
                "response": "What would you like to know about the Grateful Dead?",
                "session_id": session_id
            })
        
        # Get or create conversation history
        if session_id not in conversations:
            conversations[session_id] = {
                'history': [],
                'last_activity': datetime.now()
            }
        
        # Clean up old conversations occasionally
        if len(conversations) > 100:
            cleanup_old_conversations()
        
        # Get conversation history
        conversation_history = conversations[session_id]['history']
        
        # Generate response with conversation context
        bot_response = chatbot.chat(user_message, conversation_history)
        
        # Update conversation history
        conversations[session_id]['history'].extend([
            {'role': 'user', 'content': user_message, 'timestamp': datetime.now().isoformat()},
            {'role': 'assistant', 'content': bot_response, 'timestamp': datetime.now().isoformat()}
        ])
        conversations[session_id]['last_activity'] = datetime.now()
        
        # Keep only last 20 messages (10 exchanges) to prevent memory issues
        if len(conversations[session_id]['history']) > 20:
            conversations[session_id]['history'] = conversations[session_id]['history'][-20:]
        
        return jsonify({
            "response": bot_response,
            "session_id": session_id,
            "conversation_length": len(conversations[session_id]['history'])
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/conversation/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id and session_id in conversations:
            del conversations[session_id]
            return jsonify({"message": "Conversation cleared"})
        else:
            return jsonify({"message": "No conversation found"})
            
    except Exception as e:
        return jsonify({
            "error": f"Error clearing conversation: {str(e)}"
        }), 500

@app.route('/knowledge/stats', methods=['GET'])
def knowledge_stats():
    """Get knowledge base statistics"""
    try:
        count = chatbot.collection.count()
        return jsonify({
            "total_documents": count,
            "categories": ["band_members", "songs", "shows", "albums", "culture"],
            "active_conversations": len(conversations)
        })
    except Exception as e:
        return jsonify({
            "error": f"Could not get stats: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("\n🌹💀🌹 Starting Grateful Dead Chatbot API with Memory 🌹💀🌹")
    print("API will be available at: http://localhost:5000")
    print("Features: Conversation memory, session management")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
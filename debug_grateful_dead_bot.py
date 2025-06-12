import os
import json
import pickle
from typing import List, Dict, Any
import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import openai
from datetime import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GratefulDeadChatbot:
    def __init__(self, openai_api_key: str):
        """Initialize the Grateful Dead RAG chatbot"""
        print("🔧 Initializing chatbot...")
        
        if not openai_api_key:
            raise ValueError("OpenAI API key is required!")
        
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        print("✓ OpenAI client initialized")
        
        # Initialize embedding model
        print("📥 Loading embedding model (this may take a few minutes on first run)...")
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            raise
        
        # Initialize vector database
        print("🗄️ Initializing vector database...")
        try:
            self.chroma_client = chromadb.PersistentClient(path="./dead_knowledge_db")
            self.collection = self.chroma_client.get_or_create_collection(
                name="grateful_dead_knowledge",
                metadata={"description": "Grateful Dead knowledge base"}
            )
            print("✓ Vector database initialized")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise
        
        print("🎸 Chatbot initialized successfully!")
    
    def add_knowledge_to_db(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector database"""
        print(f"📚 Adding {len(documents)} documents to knowledge base...")
        
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            text = doc['content']
            metadata = {k: v for k, v in doc.items() if k != 'content'}
            
            texts.append(text)
            metadatas.append(metadata)
            ids.append(f"doc_{i}_{hash(text) % 100000}")
        
        try:
            # Generate embeddings
            print("🧠 Generating embeddings...")
            embeddings = self.embedding_model.encode(texts).tolist()
            print("✓ Embeddings generated")
            
            # Add to ChromaDB
            print("💾 Adding to database...")
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            print("✓ Documents added to knowledge base!")
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            raise
    
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
            print(f"❌ Error searching knowledge base: {e}")
            return []
    
    def generate_response(self, user_query: str, context_docs: List[Dict]) -> str:
        """Generate response using OpenAI with retrieved context"""
        
        # Build context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in context_docs])
        
        system_prompt = """You are the ultimate Grateful Dead expert and enthusiast! You have deep knowledge about:
        - All Grateful Dead songs, albums, and performances
        - Band members past and present (Jerry Garcia, Bob Weir, Phil Lesh, etc.)
        - Tour history, venues, and memorable shows
        - The Dead community and culture
        - Related bands and solo projects
        
        Use the provided context to answer questions accurately. If you're not sure about something, say so.
        Keep the vibe conversational and friendly - like talking to a fellow Deadhead.
        Use Grateful Dead terminology and references naturally when appropriate.
        
        Context information:
        {context}
        """
        
        user_prompt = f"Question: {user_query}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt.format(context=context)},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Sorry, I'm having trouble connecting to OpenAI right now. Error: {str(e)}"
    
    def chat(self, user_input: str) -> str:
        """Main chat method"""
        if not user_input.strip():
            return "What would you like to know about the Grateful Dead?"
        
        # Search for relevant context
        relevant_docs = self.search_knowledge(user_input)
        
        # Generate response
        response = self.generate_response(user_input, relevant_docs)
        
        return response

def create_sample_knowledge_base():
    """Create sample Grateful Dead knowledge base"""
    sample_docs = [
        {
            "content": "Jerry Garcia was the lead guitarist and primary songwriter for the Grateful Dead. Born Jerome John Garcia on August 1, 1942, in San Francisco, he was known for his distinctive guitar playing style and improvisational skills. Jerry played a variety of guitars throughout his career, most famously 'Tiger' and 'Wolf' custom guitars built by Doug Irwin.",
            "category": "band_members",
            "person": "Jerry Garcia",
            "type": "biography"
        },
        {
            "content": "Dark Star is one of the Grateful Dead's most famous and experimental songs. Written by Jerry Garcia and Robert Hunter, it became a vehicle for extended improvisation during live performances. The song was first performed on October 29, 1966, and appeared on the Live/Dead album in 1969.",
            "category": "songs",
            "song": "Dark Star",
            "writers": "Garcia/Hunter",
            "type": "song_info"
        },
        {
            "content": "The Grateful Dead's performance at Barton Hall, Cornell University on May 8, 1977, is considered one of their greatest shows ever. The second set featured an incredible Scarlet Begonias > Fire on the Mountain, and the show has been called 'the best Dead show ever' by many fans.",
            "category": "shows",
            "venue": "Barton Hall",
            "date": "1977-05-08",
            "type": "show_review"
        },
        {
            "content": "American Beauty, released in 1970, is often considered the Grateful Dead's masterpiece studio album. It includes classics like 'Ripple,' 'Friend of the Devil,' 'Sugar Magnolia,' and 'Truckin'.' The album showcased the band's songwriting partnership between Jerry Garcia and Robert Hunter.",
            "category": "albums",
            "album": "American Beauty",
            "year": "1970",
            "type": "album_info"
        },
        {
            "content": "Deadheads are the devoted fans of the Grateful Dead, known for following the band on tour and creating a unique community culture. The term encompasses the culture of peace, love, and music that surrounded the band. Many Deadheads would travel from show to show, creating a traveling community.",
            "category": "culture",
            "topic": "Deadheads",
            "type": "culture_info"
        },
        {
            "content": "Phil Lesh played bass for the Grateful Dead and was known for his innovative, melodic bass playing style. Born Philip Chapman Lesh on March 15, 1940, he brought a classical music background to the band and often played bass lines that were more like lead parts.",
            "category": "band_members",
            "person": "Phil Lesh",
            "type": "biography"
        },
        {
            "content": "Truckin' is one of the Grateful Dead's most recognizable songs and their only top 40 hit. Written by Jerry Garcia, Bob Weir, Phil Lesh, and Robert Hunter, it appeared on American Beauty in 1970. The song references many places the band toured and includes the famous line 'What a long strange trip it's been.'",
            "category": "songs",
            "song": "Truckin'",
            "album": "American Beauty",
            "type": "song_info"
        }
    ]
    
    return sample_docs

def main():
    print("🌹💀🌹 Starting Grateful Dead Chatbot Setup 🌹💀🌹\n")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        print("Please check your .env file contains:")
        print("OPENAI_API_KEY=your-actual-key-here")
        return
    else:
        print(f"✓ Found API key: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Initialize chatbot
        print("\n🤖 Initializing chatbot...")
        chatbot = GratefulDeadChatbot(api_key)
        
        # Check if we need to populate the knowledge base
        print("\n📊 Checking knowledge base...")
        try:
            count = chatbot.collection.count()
            print(f"Found {count} documents in knowledge base")
            
            if count == 0:
                print("📥 Populating knowledge base with sample data...")
                sample_docs = create_sample_knowledge_base()
                chatbot.add_knowledge_to_db(sample_docs)
        except Exception as e:
            print(f"🆕 Creating new knowledge base... ({e})")
            sample_docs = create_sample_knowledge_base()
            chatbot.add_knowledge_to_db(sample_docs)
        
        print("\n🎸 Chatbot ready! Starting chat interface...\n")
        print("🌹💀🌹 Welcome to the Grateful Dead Chatbot! 🌹💀🌹")
        print("Ask me anything about the Dead! Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("Thanks for chatting! Keep on truckin'! ⚡")
                    break
                
                if user_input:
                    print("🤔 Thinking...")
                    response = chatbot.chat(user_input)
                    print(f"\nDead Bot: {response}\n")
                    
            except KeyboardInterrupt:
                print("\n\nThanks for chatting! Keep on truckin'! ⚡")
                break
            except Exception as e:
                print(f"❌ Error during chat: {e}")
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("Check your setup and try again!")

if __name__ == "__main__":
    main()
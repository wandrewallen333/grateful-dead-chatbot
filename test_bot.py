import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
try:
    from sentence_transformers import SentenceTransformer
    print("✓ SentenceTransformers imported successfully")
except ImportError as e:
    print(f"✗ Error importing SentenceTransformers: {e}")

try:
    import chromadb
    print("✓ ChromaDB imported successfully")
except ImportError as e:
    print(f"✗ Error importing ChromaDB: {e}")

try:
    import openai
    print("✓ OpenAI imported successfully")
except ImportError as e:
    print(f"✗ Error importing OpenAI: {e}")

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("✓ OpenAI API key found")
else:
    print("✗ OpenAI API key not found - check your .env file")

print("\nIf all checks passed, you're ready to run the chatbot!")
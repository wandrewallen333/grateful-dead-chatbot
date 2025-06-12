# 🌹💀⚡ Grateful Dead RAG Chatbot

An AI-powered chatbot that's an expert on all things Grateful Dead! Built with RAG (Retrieval-Augmented Generation) technology, it combines a comprehensive knowledge base with conversational AI to answer questions about the Dead's music, history, shows, and culture.

## Features

- 🎸 **Comprehensive Dead Knowledge**: Band members, songs, albums, shows, and culture
- 🧠 **RAG Technology**: Vector database + LLM for accurate, contextual responses  
- 💬 **Conversation Memory**: Remembers context for natural follow-up questions
- 🌐 **Web Data Integration**: Pulls real data from MusicBrainz, Archive.org
- ⚡ **Beautiful React Frontend**: Modern, responsive web interface
- 🔌 **Flask API Backend**: RESTful API with session management

## Demo

Ask questions like:
- "Tell me about Jerry Garcia"
- "What's the best version of Dark Star?"
- "What happened at the Barton Hall show?"
- "What albums should I start with?"

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Flask API      │    │  Vector Database│
│   (Port 3000)  │◄──►│   (Port 5000)    │◄──►│   (ChromaDB)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   OpenAI GPT     │
                       │   + Web Sources  │
                       └──────────────────┘
```

## Quick Start

### 1. Clone and Setup Backend

```bash
git clone https://github.com/yourusername/grateful-dead-chatbot.git
cd grateful-dead-chatbot

# Create virtual environment
python -m venv dead_bot_env
source dead_bot_env/bin/activate  # On Windows: dead_bot_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and add billing info
3. Generate an API key
4. Add it to your `.env` file

### 3. Start Backend

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 4. Setup Frontend

```bash
cd dead-chatbot-frontend
npm install
npm start
```

The React app will open at `http://localhost:3000`

## API Endpoints

- `GET /health` - Health check and status
- `POST /chat` - Send message and get response
- `POST /conversation/clear` - Clear conversation history
- `GET /knowledge/stats` - Knowledge base statistics

## Knowledge Base

The chatbot includes:

- **Band Members**: Jerry Garcia, Bob Weir, Phil Lesh, Mickey Hart, Bill Kreutzmann, and more
- **Classic Songs**: Dark Star, Truckin', Ripple, Fire on the Mountain, etc.
- **Albums**: American Beauty, Workingman's Dead, Live/Dead, and more
- **Famous Shows**: Barton Hall '77, Europe '72, Woodstock, etc.
- **Culture**: Deadheads, taping culture, symbols, and community
- **Live Data**: Real albums from MusicBrainz, shows from Archive.org

## Development

### Adding Knowledge

```python
# Add new documents to the knowledge base
new_docs = [
    {
        "content": "Your Dead knowledge here...",
        "category": "songs",  # or "shows", "band_members", etc.
        "type": "song_info"
    }
]
chatbot.add_knowledge_to_db(new_docs)
```

### Project Structure

```
grateful-dead-chatbot/
├── app.py                      # Flask API with conversation memory
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── dead-chatbot-frontend/     # React frontend
│   ├── src/App.js            # Main React component
│   ├── src/App.css           # Styling
│   └── package.json          # Node dependencies
└── dead_knowledge_db/        # Vector database (auto-created)
```

## Technology Stack

**Backend:**
- Python 3.9+
- Flask (API framework)
- OpenAI GPT-3.5-turbo (LLM)
- ChromaDB (vector database)
- SentenceTransformers (embeddings)
- BeautifulSoup (web scraping)

**Frontend:**
- React 18
- Lucide React (icons)
- Modern CSS with gradients and animations

**Data Sources:**
- MusicBrainz API (official discography)
- Archive.org (live recordings)
- Curated Dead knowledge

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Enhancement

- [ ] Add Spotify integration for music recommendations
- [ ] Include lyrics database
- [ ] Add setlist.fm API integration
- [ ] Implement voice interface
- [ ] Add image recognition for Dead memorabilia
- [ ] Create mobile app version
- [ ] Add more data sources (Dead.net, etc.)

## License

MIT License - see LICENSE file for details

## Acknowledgments

- The Grateful Dead for the endless inspiration 🌹
- Archive.org for preserving the music
- The Deadhead community for keeping the spirit alive
- OpenAI for making this kind of AI accessible

---

**"What a long strange trip it's been!"** - Truckin', 1970

## Support

If you have issues:
1. Check that your OpenAI API key is valid and has billing set up
2. Make sure both Flask (port 5000) and React (port 3000) are running
3. Check the console for error messages
4. Open an issue on GitHub

Keep on truckin'! ⚡
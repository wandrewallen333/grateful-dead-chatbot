import requests
import json
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
from datetime import datetime

class GratefulDeadDataScraper:
    """Scrape and fetch Grateful Dead data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_setlistfm_data(self, artist_mbid="6faa7ca7-0d99-4a5e-bfa6-1fd5037520c6", api_key=None):
        """
        Fetch setlist data from setlist.fm API
        You need a free API key from setlist.fm
        """
        if not api_key:
            print("⚠️ No setlist.fm API key provided. Get one free at https://www.setlist.fm/settings/api")
            return []
        
        url = f"https://api.setlist.fm/rest/1.0/artist/{artist_mbid}/setlists"
        headers = {
            'Accept': 'application/json',
            'x-api-key': api_key
        }
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            setlists = []
            for setlist in data.get('setlist', []):
                setlist_doc = self.parse_setlist_data(setlist)
                if setlist_doc:
                    setlists.append(setlist_doc)
            
            print(f"✓ Fetched {len(setlists)} setlists from setlist.fm")
            return setlists
            
        except Exception as e:
            print(f"❌ Error fetching setlist.fm data: {e}")
            return []
    
    def parse_setlist_data(self, setlist_data):
        """Parse individual setlist into document format"""
        try:
            date = setlist_data.get('eventDate', '')
            venue = setlist_data.get('venue', {})
            venue_name = venue.get('name', 'Unknown Venue')
            city = venue.get('city', {}).get('name', '')
            
            # Extract songs from sets
            songs = []
            sets = setlist_data.get('sets', {}).get('set', [])
            for set_data in sets:
                for song in set_data.get('song', []):
                    songs.append(song.get('name', ''))
            
            content = f"Grateful Dead performed at {venue_name} in {city} on {date}. "
            if songs:
                content += f"Setlist included: {', '.join(songs[:10])}"  # First 10 songs
                if len(songs) > 10:
                    content += f" and {len(songs) - 10} more songs."
            
            return {
                'content': content,
                'category': 'shows',
                'date': date,
                'venue': venue_name,
                'city': city,
                'songs': songs,
                'type': 'setlist_data'
            }
        except Exception as e:
            print(f"Error parsing setlist: {e}")
            return None
    
    def scrape_dead_net_archives(self):
        """Scrape show information from archive.org"""
        url = "https://archive.org/advancedsearch.php"
        params = {
            'q': 'collection:GratefulDead AND mediatype:etree',
            'fl[]': ['identifier', 'title', 'date', 'description'],
            'sort[]': 'date desc',
            'rows': 50,
            'page': 1,
            'output': 'json'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            shows = []
            for doc in data.get('response', {}).get('docs', []):
                show_doc = self.parse_archive_show(doc)
                if show_doc:
                    shows.append(show_doc)
            
            print(f"✓ Scraped {len(shows)} shows from archive.org")
            return shows
            
        except Exception as e:
            print(f"❌ Error scraping archive.org: {e}")
            return []
    
    def parse_archive_show(self, doc):
        """Parse archive.org show data"""
        try:
            title = doc.get('title', '')
            date = doc.get('date', '')
            description = doc.get('description', [''])[0] if doc.get('description') else ''
            identifier = doc.get('identifier', '')
            
            # Extract venue info from title if possible
            venue_match = re.search(r'at (.+?) on', title) or re.search(r'- (.+?) -', title)
            venue = venue_match.group(1) if venue_match else 'Unknown Venue'
            
            content = f"Grateful Dead show from {date}"
            if venue != 'Unknown Venue':
                content += f" at {venue}"
            if description:
                content += f". {description[:200]}"  # First 200 chars of description
            
            return {
                'content': content,
                'category': 'shows',
                'date': date,
                'venue': venue,
                'archive_id': identifier,
                'type': 'archive_show'
            }
        except Exception as e:
            print(f"Error parsing archive show: {e}")
            return None
    
    def scrape_dead_essays_lyrics(self):
        """Scrape song information and essays from various Dead sites"""
        # This is a simplified example - you'd want to expand this
        
        song_info = [
            {
                'content': 'The Grateful Dead performed over 2,300 concerts during their 30-year career from 1965 to 1995. They were known for never playing the same setlist twice, making each show unique. The band averaged about 75 shows per year during their peak touring years.',
                'category': 'statistics', 
                'type': 'general_info'
            },
            {
                'content': 'Robert Hunter was the primary lyricist for the Grateful Dead, writing words to most of Jerry Garcia\'s compositions. Hunter\'s poetic, often mystical lyrics became a defining element of the Dead\'s music. Songs like "Ripple," "Truckin\'," and "Fire on the Mountain" showcase his unique writing style.',
                'category': 'band_members',
                'person': 'Robert Hunter',
                'type': 'biography'
            },
            {
                'content': 'The Grateful Dead\'s improvisational style was influenced by jazz, bluegrass, country, folk, blues, and psychedelic rock. Their jams could extend songs from 3 minutes to over 30 minutes, with "Dark Star" being the most famous example of their exploratory approach to music.',
                'category': 'musical_style',
                'type': 'analysis'
            }
        ]
        
        return song_info
    
    def get_musicbrainz_data(self):
        """Fetch structured data from MusicBrainz API (free, no key needed)"""
        # Grateful Dead's MusicBrainz ID
        artist_id = "6faa7ca7-0d99-4a5e-bfa6-1fd5037520c6"
        
        try:
            # Get releases (albums)
            releases_url = f"https://musicbrainz.org/ws/2/release?artist={artist_id}&type=album&status=official&limit=25&fmt=json"
            response = self.session.get(releases_url)
            response.raise_for_status()
            releases_data = response.json()
            
            albums = []
            for release in releases_data.get('releases', []):
                album_doc = {
                    'content': f"{release.get('title', '')} is a Grateful Dead album released in {release.get('date', '')[:4] if release.get('date') else 'unknown year'}. {release.get('disambiguation', '')}",
                    'category': 'albums',
                    'album': release.get('title', ''),
                    'year': release.get('date', '')[:4] if release.get('date') else None,
                    'type': 'album_info'
                }
                albums.append(album_doc)
            
            print(f"✓ Fetched {len(albums)} albums from MusicBrainz")
            return albums
            
        except Exception as e:
            print(f"❌ Error fetching MusicBrainz data: {e}")
            return []
    
    def get_all_external_data(self, setlistfm_api_key=None):
        """Fetch data from all available sources"""
        print("🌐 Fetching Grateful Dead data from external sources...")
        
        all_docs = []
        
        # MusicBrainz (no API key needed)
        mb_data = self.get_musicbrainz_data()
        all_docs.extend(mb_data)
        
        # Archive.org
        archive_data = self.scrape_dead_net_archives()
        all_docs.extend(archive_data)
        
        # Additional curated content
        curated_data = self.scrape_dead_essays_lyrics()
        all_docs.extend(curated_data)
        
        # Setlist.fm (requires API key)
        if setlistfm_api_key:
            setlist_data = self.get_setlistfm_data(api_key=setlistfm_api_key)
            all_docs.extend(setlist_data)
        else:
            print("💡 Tip: Get a free setlist.fm API key for setlist data!")
        
        print(f"🎸 Total documents fetched: {len(all_docs)}")
        return all_docs

def add_external_data_to_chatbot(chatbot, setlistfm_api_key=None):
    """Add external data to your existing chatbot"""
    scraper = GratefulDeadDataScraper()
    
    print("🌍 Gathering data from the internet...")
    external_docs = scraper.get_all_external_data(setlistfm_api_key)
    
    if external_docs:
        print(f"📚 Adding {len(external_docs)} documents from external sources...")
        chatbot.add_knowledge_to_db(external_docs)
        print("✅ External data added successfully!")
        
        print("\n🎵 Your chatbot now includes:")
        print("- Official album discography from MusicBrainz")
        print("- Live show recordings from Archive.org")
        print("- Additional Dead knowledge and statistics")
        if setlistfm_api_key:
            print("- Recent setlist data from setlist.fm")
        
        return len(external_docs)
    else:
        print("❌ No external data could be fetched")
        return 0

# Example usage function
def enhance_chatbot_with_web_data(chatbot, setlistfm_key=None):
    """Main function to enhance your chatbot with web data"""
    print("🚀 Enhancing your Grateful Dead chatbot with internet data...")
    
    # Add external data
    docs_added = add_external_data_to_chatbot(chatbot, setlistfm_key)
    
    if docs_added > 0:
        # Test the enhanced knowledge
        print("\n🧪 Testing enhanced knowledge...")
        test_queries = [
            "What albums did the Grateful Dead release?",
            "Tell me about recent Dead shows",
            "What's the difference between studio and live Dead music?"
        ]
        
        for query in test_queries:
            print(f"\nTest: {query}")
            response = chatbot.chat(query)
            print(f"Response: {response[:150]}...")
    
    return docs_added

if __name__ == "__main__":
    # Example of how to use this with your chatbot
    print("This script enhances your Grateful Dead chatbot with internet data!")
    print("\nTo use:")
    print("1. Get a free API key from https://www.setlist.fm/settings/api (optional)")
    print("2. Import your chatbot: from your_bot_file import GratefulDeadChatbot")
    print("3. Run: enhance_chatbot_with_web_data(your_chatbot, 'your_setlist_api_key')")
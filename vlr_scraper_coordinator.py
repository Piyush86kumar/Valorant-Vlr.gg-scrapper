import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from matches_scraper import MatchesScraper
from player_stats_scraper import PlayerStatsScraper
from maps_agents_scraper import MapsAgentsScraper

class VLRScraperCoordinator:
    """
    Main coordinator for VLR.gg scraping operations
    Orchestrates the three specialized scrapers: matches, player stats, and maps/agents
    """
    
    def __init__(self):
        self.matches_scraper = MatchesScraper()
        self.stats_scraper = PlayerStatsScraper()
        self.maps_agents_scraper = MapsAgentsScraper()

    def validate_url(self, url: str) -> tuple[bool, str]:
        """Validate VLR.gg event URL"""
        if not url:
            return False, "Please enter a URL"

        if not re.match(r'https?://www\.vlr\.gg/event/\d+/', url):
            return False, "Invalid VLR.gg event URL format. Expected: https://www.vlr.gg/event/{id}/{name}"

        try:
            import requests
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                return True, "Valid URL"
            else:
                return False, f"URL returned status {response.status_code}"
        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"

    def extract_event_info(self, main_url: str) -> Dict[str, Any]:
        """Extract basic event information from main event page"""
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(main_url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            event_info = {
                'url': main_url,
                'scraped_at': datetime.now().isoformat()
            }

            # Title
            title_elem = soup.find('h1', class_='wf-title')
            if title_elem:
                event_info['title'] = title_elem.get_text(strip=True)

            # Subtitle
            subtitle_elem = soup.find('h2', class_='event-desc-subtitle')
            if subtitle_elem:
                event_info['subtitle'] = subtitle_elem.get_text(strip=True)

            # Description items
            item_blocks = soup.select('div.event-desc-item')
            for block in item_blocks:
                label = block.find('div', class_='event-desc-item-label')
                value = block.find('div', class_='event-desc-item-value')
                if not label or not value:
                    continue

                label_text = label.get_text(strip=True).lower()
                value_text = value.get_text(strip=True)

                if 'date' in label_text:
                    event_info['dates'] = value_text
                elif 'location' in label_text:
                    event_info['location'] = value_text
                elif 'prize' in label_text:
                    event_info['prize_pool'] = value_text

            return event_info

        except Exception as e:
            return {
                'url': main_url,
                'error': f"Error extracting event info: {e}",
                'scraped_at': datetime.now().isoformat()
            }

    
    def scrape_matches_only(self, main_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Scrape only matches data"""
        try:
            if progress_callback:
                progress_callback("Starting matches scraping...")
            
            matches_data = self.matches_scraper.scrape_matches(main_url, progress_callback)
            
            return {
                'event_info': self.extract_event_info(main_url),
                'matches_data': matches_data,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error scraping matches: {e}")
    
    def scrape_player_stats_only(self, main_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Scrape only player statistics"""
        try:
            if progress_callback:
                progress_callback("Starting player stats scraping...")
            
            stats_data = self.stats_scraper.scrape_player_stats(main_url, progress_callback)
            
            return {
                'event_info': self.extract_event_info(main_url),
                'stats_data': stats_data,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error scraping player stats: {e}")
    
    def scrape_maps_agents_only(self, main_url: str, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Scrape only maps and agents data"""
        try:
            if progress_callback:
                progress_callback("Starting maps and agents scraping...")
            
            maps_agents_data = self.maps_agents_scraper.scrape_maps_and_agents(main_url, progress_callback)
            
            return {
                'event_info': self.extract_event_info(main_url),
                'maps_agents_data': maps_agents_data,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Error scraping maps and agents: {e}")
    
    def scrape_comprehensive(self, main_url: str, 
                           scrape_matches: bool = True,
                           scrape_stats: bool = True, 
                           scrape_maps_agents: bool = True,
                           progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scrape comprehensive data using selected scrapers
        """
        try:
            if progress_callback:
                progress_callback("Initializing comprehensive scraping...")
            
            # Initialize result structure
            result = {
                'event_info': {},
                'matches_data': {},
                'stats_data': {},
                'maps_agents_data': {},
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract event info
            if progress_callback:
                progress_callback("Extracting event information...")
            result['event_info'] = self.extract_event_info(main_url)
            
            # Scrape matches if requested
            if scrape_matches:
                if progress_callback:
                    progress_callback("Scraping matches data...")
                result['matches_data'] = self.matches_scraper.scrape_matches(main_url, progress_callback)
            
            # Scrape player stats if requested
            if scrape_stats:
                if progress_callback:
                    progress_callback("Scraping player statistics...")
                result['stats_data'] = self.stats_scraper.scrape_player_stats(main_url, progress_callback)
            
            # Scrape maps and agents if requested
            if scrape_maps_agents:
                if progress_callback:
                    progress_callback("Scraping maps and agents data...")
                result['maps_agents_data'] = self.maps_agents_scraper.scrape_maps_and_agents(main_url, progress_callback)
            
            if progress_callback:
                progress_callback("Comprehensive scraping completed!")
            
            return result
            
        except Exception as e:
            raise Exception(f"Error in comprehensive scraping: {e}")
    
    def get_scraping_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of scraped data"""
        try:
            summary = {
                'event_title': data.get('event_info', {}).get('title', 'Unknown'),
                'total_matches': 0,
                'total_players': 0,
                'total_agents': 0,
                'total_maps': 0,
                'teams_count': 0,
                'scraped_sections': []
            }
            
            # Count matches
            matches_data = data.get('matches_data', {})
            if matches_data:
                summary['total_matches'] = matches_data.get('total_matches', 0)
                summary['scraped_sections'].append('Matches')
                
                # Count unique teams from matches
                matches = matches_data.get('matches', [])
                teams = set()
                for match in matches:
                    teams.add(match.get('team1', ''))
                    teams.add(match.get('team2', ''))
                teams.discard('')
                summary['teams_count'] = len(teams)
            
            # Count players
            stats_data = data.get('stats_data', {})
            if stats_data:
                summary['total_players'] = stats_data.get('total_players', 0)
                summary['scraped_sections'].append('Player Stats')
            
            # Count agents and maps
            maps_agents_data = data.get('maps_agents_data', {})
            if maps_agents_data:
                summary['total_agents'] = maps_agents_data.get('total_agents', 0)
                summary['total_maps'] = maps_agents_data.get('total_maps', 0)
                summary['scraped_sections'].append('Maps & Agents')
            
            return summary
            
        except Exception:
            return {
                'event_title': 'Unknown',
                'total_matches': 0,
                'total_players': 0,
                'total_agents': 0,
                'total_maps': 0,
                'teams_count': 0,
                'scraped_sections': []
            }
    
    def save_to_json(self, data: Dict[str, Any], filename_prefix: str = 'vlr_data') -> str:
        """Save scraped data to JSON file"""
        try:
            import json
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{filename_prefix}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Error saving to JSON: {e}")


# Example usage and testing
if __name__ == "__main__":
    coordinator = VLRScraperCoordinator()
    
    # Test URL
    test_url = "https://www.vlr.gg/event/2097/valorant-champions-2024"
    
    print("🎮 VLR Scraper Coordinator Test")
    print("=" * 50)
    
    try:
        # Validate URL
        is_valid, message = coordinator.validate_url(test_url)
        print(f"URL Validation: {'✅' if is_valid else '❌'} {message}")
        
        if not is_valid:
            exit(1)
        
        def progress_callback(message):
            print(f"📊 {message}")
        
        # Test individual scrapers
        print("\n🧪 Testing Individual Scrapers:")
        print("-" * 30)
        
        # Test matches scraper
        print("1. Testing Matches Scraper...")
        matches_result = coordinator.scrape_matches_only(test_url, progress_callback)
        print(f"   ✅ Matches: {matches_result['matches_data'].get('total_matches', 0)}")
        
        # Test player stats scraper
        print("\n2. Testing Player Stats Scraper...")
        stats_result = coordinator.scrape_player_stats_only(test_url, progress_callback)
        print(f"   ✅ Players: {stats_result['stats_data'].get('total_players', 0)}")
        
        # Test maps/agents scraper
        print("\n3. Testing Maps & Agents Scraper...")
        maps_result = coordinator.scrape_maps_agents_only(test_url, progress_callback)
        print(f"   ✅ Agents: {maps_result['maps_agents_data'].get('total_agents', 0)}")
        print(f"   ✅ Maps: {maps_result['maps_agents_data'].get('total_maps', 0)}")
        
        # Test comprehensive scraping
        print("\n🚀 Testing Comprehensive Scraping:")
        print("-" * 30)
        
        comprehensive_data = coordinator.scrape_comprehensive(
            test_url, 
            scrape_matches=True,
            scrape_stats=True, 
            scrape_maps_agents=True,
            progress_callback=progress_callback
        )
        
        # Get summary
        summary = coordinator.get_scraping_summary(comprehensive_data)
        
        print(f"\n📊 SCRAPING SUMMARY:")
        print(f"   📋 Event: {summary['event_title']}")
        print(f"   🏆 Matches: {summary['total_matches']}")
        print(f"   👥 Players: {summary['total_players']}")
        print(f"   🎭 Agents: {summary['total_agents']}")
        print(f"   🗺️ Maps: {summary['total_maps']}")
        print(f"   🏅 Teams: {summary['teams_count']}")
        print(f"   📦 Sections: {', '.join(summary['scraped_sections'])}")
        
        # Save data
        filename = coordinator.save_to_json(comprehensive_data)
        print(f"\n💾 Data saved to: {filename}")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

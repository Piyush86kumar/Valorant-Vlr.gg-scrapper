#!/usr/bin/env python3
"""
Detailed Match Scraper for VLR.gg
Scrapes comprehensive match details from individual match pages
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class DetailedMatchScraper:
    """
    Scraper for detailed match information from VLR.gg match pages
    Extracts comprehensive match data including maps, scores, players, and statistics
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        # Selenium options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')

    def _get_rendered_html(self, url: str) -> str:
        """Use Selenium to fetch the fully rendered HTML of the page."""
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            driver.get(url)
            # Wait for the match header and at least one stats table to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'match-header'))
            )
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'vm-stats-game'))
            )
            time.sleep(2)  # Give extra time for JS to load tables
            html = driver.page_source
            return html
        finally:
            driver.quit()
    
    def scrape_match(self, url: str) -> Dict[str, Any]:
        """Scrape detailed match data from a VLR.gg match page using Selenium for rendering."""
        try:
            html = self._get_rendered_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            # Extract basic match info
            match_data = self._extract_match_info(soup, url)
            # Extract map details and player stats
            map_data = self._extract_map_details(soup)
            match_data['maps'] = map_data
            return match_data
        except Exception as e:
            print(f"Error scraping match: {str(e)}")
            return {}
    
    def extract_match_id_from_url(self, match_url: str) -> Optional[str]:
        """Extract match ID from VLR.gg match URL"""
        try:
            # Pattern: https://www.vlr.gg/378660/fnatic-vs-kr-esports-valorant-champions-2024-decider-a
            match = re.search(r'/(\d+)/', match_url)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
    
    def _extract_match_info(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract basic match information from the header."""
        match_data = {
            'match_url': url,
            'match_id': self.extract_match_id_from_url(url),
            'match_date': None,
            'event_name': None,
            'team1_name': None,
            'team2_name': None,
            'team1_score': None,
            'team2_score': None,
            'team1_id': None,
            'team2_id': None,
            'format': None,
            'patch': None
        }
        
        # Get match header
        header = soup.find('div', class_='match-header')
        if header:
            # Extract event name
            event_elem = header.find('a', class_='match-header-event')
            if event_elem:
                match_data['event_name'] = self._clean_text(event_elem.text)
            
            # Extract date
            date_elem = header.find('div', class_='moment-tz-convert')
            if date_elem:
                match_data['match_date'] = self._clean_text(date_elem.text)
            
            # Extract patch
            patch_elem = header.find('div', string=lambda x: x and 'Patch' in x)
            if patch_elem:
                match_data['patch'] = self._clean_text(patch_elem.text).replace('Patch', '').strip()
            
            # Extract team names and scores
            teams = header.find_all('div', class_='team')
            if len(teams) >= 2:
                # Team 1
                team1 = teams[0]
                team1_name = team1.find('div', class_='team-name')
                if team1_name:
                    match_data['team1_name'] = self._clean_text(team1_name.text)
                team1_id = team1.find('div', class_='team-id')
                if team1_id:
                    match_data['team1_id'] = self._clean_text(team1_id.text).strip('[]')
                
                # Team 2
                team2 = teams[1]
                team2_name = team2.find('div', class_='team-name')
                if team2_name:
                    match_data['team2_name'] = self._clean_text(team2_name.text)
                team2_id = team2.find('div', class_='team-id')
                if team2_id:
                    match_data['team2_id'] = self._clean_text(team2_id.text).strip('[]')
                
                # Scores
                scores = header.find_all('div', class_='score')
                if len(scores) >= 2:
                    match_data['team1_score'] = self._clean_text(scores[0].text)
                    match_data['team2_score'] = self._clean_text(scores[1].text)
            
            # Extract format
            format_elem = header.find('div', string=lambda x: x and 'Bo' in x)
            if format_elem:
                match_data['format'] = self._clean_text(format_elem.text)
        
        return match_data
    
    def _extract_map_details(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract details for each map in the match."""
        maps_data = []
        
        # Find all map containers
        map_containers = soup.find_all('div', class_='vm-stats-game')
        
        for container in map_containers:
            game_id = container.get('data-game-id', 'unknown')
            if game_id == 'all':  # Skip the overall stats container
                continue
                
            map_data = {
                'game_id': game_id,
                'map_name': None,
                'team1_score': None,
                'team2_score': None,
                'pick_team': None,
                'player_stats': []
            }
            
            # Get map name and pick info
            map_header = container.find('div', class_='vm-stats-game-header')
            if map_header:
                map_name = map_header.find('div', class_='map')
                if map_name:
                    # Extract just the map name (before PICK/BAN)
                    map_text = self._clean_text(map_name.text)
                    map_data['map_name'] = map_text.split('PICK')[0].strip()
                
                # Get pick info
                pick_info = map_header.find('div', string=lambda x: x and 'PICK' in x)
                if pick_info:
                    team_name = pick_info.find_previous('div', class_='team-name')
                    if team_name:
                        map_data['pick_team'] = self._clean_text(team_name.text)
            
            # Get scores
            scores = container.find_all('div', class_='score')
            if len(scores) >= 2:
                map_data['team1_score'] = self._clean_text(scores[0].text)
                map_data['team2_score'] = self._clean_text(scores[1].text)
            
            # Get player stats
            stats_tables = container.find_all('table')
            if len(stats_tables) >= 2:
                # First table is team 1, second is team 2
                for i, table in enumerate(stats_tables[:2]):
                    team_stats = self._parse_stats_table(table, i + 1)
                    map_data['player_stats'].extend(team_stats)
            
            maps_data.append(map_data)
        
        return maps_data
    
    def _parse_stats_table(self, table: BeautifulSoup, team_num: int) -> List[Dict[str, Any]]:
        """Parse a stats table for a team."""
        player_stats = []
        
        # Get headers
        headers = [self._clean_text(th.text) for th in table.find_all('th')]
        if not headers:
            return player_stats
        
        # Get all rows except header
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            
            # Extract player name and team
            player_name = self._clean_text(cells[0].text)
            # Remove team name from player name if present
            player_name = re.sub(r'\s+(MIBR|LEV|LEVIATÁN)$', '', player_name)
            
            # Create player stats dict
            stats = {
                'player_name': player_name,
                'team_number': team_num
            }
            
            # Add stats from remaining cells
            for i, cell in enumerate(cells[1:], 1):
                if i < len(headers):
                    stat_name = headers[i].lower()
                    stat_value = self._clean_text(cell.text)
                    stats[stat_name] = self._clean_stat_value(stat_value)
            
            player_stats.append(stats)
        
        return player_stats
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and newlines."""
        if not text:
            return ""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        return text.strip()
    
    def _clean_stat_value(self, value: str) -> Any:
        """Clean and convert stat values to appropriate types."""
        if not value or value == '-':
            return None
        
        # Clean the value first
        value = self._clean_text(value)
        
        # Handle percentage values
        if '%' in value:
            try:
                return float(value.replace('%', '')) / 100
            except ValueError:
                return None
        
        # Handle values with slashes (e.g., "3/4")
        if '/' in value:
            try:
                return [int(x) for x in value.split('/')]
            except ValueError:
                return value
        
        # Handle regular numbers
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def scrape_multiple_matches(self, match_urls: List[str], progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """Scrape multiple matches with progress tracking"""
        detailed_matches = []
        
        for i, match_url in enumerate(match_urls):
            try:
                if progress_callback:
                    progress_callback(f"Scraping match {i+1}/{len(match_urls)}: {match_url}")
                
                match_data = self.scrape_match(match_url)
                detailed_matches.append(match_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping match {match_url}: {e}")
                continue
        
        return detailed_matches


# Example usage and testing
if __name__ == "__main__":
    scraper = DetailedMatchScraper()
    
    # Test with a sample match URL
    test_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    
    print("🔍 Testing Detailed Match Scraper")
    print("=" * 50)
    print(f"🎯 Test URL: {test_url}")
    
    try:
        match_data = scraper.scrape_match(test_url)
        
        print(f"✅ Match scraped successfully!")
        print(f"📊 Match ID: {match_data.get('match_id')}")
        print(f"🏟️ Teams: {match_data.get('team1_name')} vs {match_data.get('team2_name')}")
        print(f"📈 Score: {match_data.get('final_score')}")
        print(f"🗺️ Maps played: {match_data.get('maps_played')}")
        
        # Save sample data
        with open('sample_detailed_match.json', 'w', encoding='utf-8') as f:
            json.dump(match_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sample data saved to 'sample_detailed_match.json'")
        
    except Exception as e:
        print(f"❌ Error: {e}")

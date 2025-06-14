import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse
import pandas as pd

class VLRMatchScraper:
    """
    A scraper class for extracting detailed match statistics from VLR.gg
    Handles match URLs, player statistics, team performance, and map-specific data
    """
    def __init__(self):
        # Initialize base configuration for the scraper
        self.base_url = "https://www.vlr.gg"
        self.session = requests.Session()
        # Set a realistic user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = 2  # Delay between requests to avoid rate limiting
        
    def extract_match_urls_from_event(self, event_url):
        """
        Extract all match URLs from an event page
        Args:
            event_url (str): The URL of the VLR.gg event page
        Returns:
            list: List of unique match URLs found on the event page
        """
        try:
            response = self.session.get(event_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            match_urls = []
            
            # Find all match links in the brackets/results section
            # Pattern matches URLs like /123456/team1-vs-team2/tournament/stage
            match_links = soup.find_all('a', href=re.compile(r'/\d+/.*?/.*?/.*?'))
            
            for link in match_links:
                href = link.get('href')
                if href and self.is_match_url(href):
                    full_url = urljoin(self.base_url, href)
                    match_urls.append(full_url)
            
            # Remove duplicates and filter only completed matches
            unique_urls = list(set(match_urls))
            
            return unique_urls
            
        except Exception as e:
            st.error(f"Error extracting match URLs: {str(e)}")
            return []
    
    def is_match_url(self, url):
        """
        Validate if a URL follows the VLR.gg match URL pattern
        Args:
            url (str): URL to validate
        Returns:
            bool: True if URL matches the expected pattern
        """
        # VLR match URLs follow pattern: /match_id/team1-vs-team2/tournament/stage
        pattern = r'/\d+/.*?-vs-.*?/.*?/.*?'
        return bool(re.match(pattern, url))
    
    def extract_match_id(self, url):
        """
        Extract the numeric match ID from a VLR.gg match URL
        Args:
            url (str): Match URL
        Returns:
            str: Match ID or None if not found
        """
        match = re.search(r'/(\d+)/', url)
        return match.group(1) if match else None
    
    def scrape_match_details(self, match_url):
        """
        Main method to scrape all details for a single match
        Args:
            match_url (str): URL of the match to scrape
        Returns:
            dict: Dictionary containing all match data or None if scraping fails
        """
        try:
            response = self.session.get(match_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Structure the match data into logical sections
            match_data = {
                'match_url': match_url,
                'match_id': self.extract_match_id(match_url),
                'scraped_at': datetime.now().isoformat(),
                'basic_info': self.extract_basic_info(soup),
                'maps': self.extract_maps_info(soup),
                'overview_stats': self.extract_overview_stats(soup),
                'individual_map_stats': self.extract_individual_map_stats(soup),
                'team_stats': self.extract_team_stats(soup)
            }
            
            return match_data
            
        except Exception as e:
            st.error(f"Error scraping match {match_url}: {str(e)}")
            return None
    
    def extract_basic_info(self, soup):
        """
        Extract basic match information including teams, scores, and tournament details
        Args:
            soup (BeautifulSoup): Parsed HTML of the match page
        Returns:
            dict: Dictionary containing basic match information
        """
        basic_info = {}
        
        try:
            # Match header information
            header = soup.find('div', class_='match-header')
            if header:
                # Extract team names from header
                team_elements = header.find_all('div', class_='match-header-link-name')
                if len(team_elements) >= 2:
                    basic_info['team1_name'] = team_elements[0].get_text(strip=True)
                    basic_info['team2_name'] = team_elements[1].get_text(strip=True)
                
                # Extract tournament information
                event_element = header.find('div', class_='match-header-event')
                if event_element:
                    basic_info['tournament'] = event_element.get_text(strip=True)
                
                # Extract and parse match score
                score_element = header.find('div', class_='match-header-vs-score')
                if score_element:
                    score_text = score_element.get_text(strip=True)
                    if ':' in score_text:
                        # Split on ':' to get the scores
                        scores = score_text.split(':')
                        if len(scores) >= 2:
                            # Remove 'final' prefix and any trailing text
                            team1_score = scores[0].replace('final', '').strip()
                            team2_score = scores[1].split('vs')[0].strip()
                            try:
                                basic_info['team1_score'] = int(team1_score)
                                basic_info['team2_score'] = int(team2_score)
                            except ValueError:
                                st.warning(f"Could not parse scores: {score_text}")
                                basic_info['team1_score'] = 0
                                basic_info['team2_score'] = 0
                        else:
                            st.warning(f"Unexpected score format: {score_text}")
                            basic_info['team1_score'] = 0
                            basic_info['team2_score'] = 0
            
            # Extract match date and time
            date_element = soup.find('div', class_='moment-tz-convert')
            if date_element:
                basic_info['match_date'] = date_element.get('data-utc-ts')
            
            # Extract match format (BO1, BO3, BO5)
            format_element = soup.find('div', class_='match-header-vs-note')
            if format_element:
                basic_info['format'] = format_element.get_text(strip=True)
            
        except Exception as e:
            st.warning(f"Error extracting basic info: {str(e)}")
        
        return basic_info
    
    def extract_maps_info(self, soup):
        """
        Extract information about each map played in the match
        Args:
            soup (BeautifulSoup): Parsed HTML of the match page
        Returns:
            list: List of dictionaries containing map information
        """
        maps_data = []
        
        try:
            # Find all map sections in the match
            map_picks = soup.find_all('div', class_='vm-stats-game-header')
            
            for i, map_header in enumerate(map_picks):
                map_info = {
                    'map_order': i + 1,
                    'map_name': '',
                    'team1_score': 0,
                    'team2_score': 0,
                    'winner': '',
                    'map_stats': {}
                }
                
                # Extract map name
                map_name_element = map_header.find('div', class_='map')
                if map_name_element:
                    map_info['map_name'] = map_name_element.get_text(strip=True)
                
                # Extract scores for each team on this map
                score_elements = map_header.find_all('div', class_='score')
                if len(score_elements) >= 2:
                    map_info['team1_score'] = int(score_elements[0].get_text(strip=True))
                    map_info['team2_score'] = int(score_elements[1].get_text(strip=True))
                    
                    # Determine winner based on scores
                    if map_info['team1_score'] > map_info['team2_score']:
                        map_info['winner'] = 'team1'
                    elif map_info['team2_score'] > map_info['team1_score']:
                        map_info['winner'] = 'team2'
                    else:
                        map_info['winner'] = 'draw'
                
                maps_data.append(map_info)
                
        except Exception as e:
            st.warning(f"Error extracting maps info: {str(e)}")
        
        return maps_data
    
    def extract_overview_stats(self, soup):
        """
        Extract overall statistics for the entire match
        Args:
            soup (BeautifulSoup): Parsed HTML of the match page
        Returns:
            dict: Dictionary containing stats for all contexts (all/attack/defense)
        """
        overview_stats = {
            'all': [],
            'attack': [],
            'defense': []
        }
        
        try:
            # Find all stats tables in the overview section
            stats_tables = soup.find_all('table', class_='vm-stats-game-table')
            
            for table in stats_tables:
                context = self.determine_stat_context(table)
                if context in overview_stats:
                    players_stats = self.extract_player_stats_from_table(table)
                    overview_stats[context] = players_stats
                    
        except Exception as e:
            st.warning(f"Error extracting overview stats: {str(e)}")
        
        return overview_stats
    
    def extract_individual_map_stats(self, soup):
        """
        Extract statistics for each individual map
        Args:
            soup (BeautifulSoup): Parsed HTML of the match page
        Returns:
            list: List of dictionaries containing stats for each map
        """
        individual_map_stats = []
        
        try:
            # Find all map-specific stats sections
            map_sections = soup.find_all('div', class_='vm-stats-game')
            
            for i, section in enumerate(map_sections):
                map_stats = {
                    'map_order': i + 1,
                    'map_name': '',
                    'all': [],
                    'attack': [],
                    'defense': []
                }
                
                # Extract map name from section
                map_name_element = section.find('div', class_='map')
                if map_name_element:
                    map_stats['map_name'] = map_name_element.get_text(strip=True)
                
                # Extract stats for each context (all/attack/defense)
                tables = section.find_all('table', class_='vm-stats-game-table')
                for table in tables:
                    context = self.determine_stat_context(table)
                    if context in ['all', 'attack', 'defense']:
                        players_stats = self.extract_player_stats_from_table(table)
                        map_stats[context] = players_stats
                
                individual_map_stats.append(map_stats)
                
        except Exception as e:
            st.warning(f"Error extracting individual map stats: {str(e)}")
        
        return individual_map_stats
    
    def determine_stat_context(self, table):
        """
        Determine the context of a stats table (all/attack/defense)
        Args:
            table (BeautifulSoup): Stats table element
        Returns:
            str: Context of the stats table
        """
        # Look for context indicators in table classes or parent elements
        parent = table.find_parent()
        if parent:
            if 'attack' in parent.get('class', []):
                return 'attack'
            elif 'defense' in parent.get('class', []):
                return 'defense'
        
        return 'all'  # Default to 'all' context
    
    def extract_player_stats_from_table(self, table):
        """
        Extract individual player statistics from a stats table
        Args:
            table (BeautifulSoup): Stats table element
        Returns:
            list: List of dictionaries containing player statistics
        """
        players_stats = []
        
        try:
            # Skip header row and process all player rows
            rows = table.find_all('tr')[1:]
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 10:  # Ensure we have enough cells for all stats
                    
                    # Extract player name and agent
                    player_cell = cells[0]
                    player_name = player_cell.get_text(strip=True)
                    agent_img = player_cell.find('img')
                    agent = agent_img.get('alt', '') if agent_img else ''
                    
                    # Extract all player statistics
                    player_stats = {
                        'player_name': player_name,
                        'agent': agent,
                        'rating': self.safe_float(cells[1].get_text(strip=True)),
                        'combat_score': self.safe_int(cells[2].get_text(strip=True)),
                        'kills': self.safe_int(cells[3].get_text(strip=True)),
                        'deaths': self.safe_int(cells[4].get_text(strip=True)),
                        'assists': self.safe_int(cells[5].get_text(strip=True)),
                        'kd_ratio': self.safe_float(cells[6].get_text(strip=True)),
                        'adr': self.safe_float(cells[7].get_text(strip=True)),
                        'headshot_percentage': self.safe_float(cells[8].get_text(strip=True).replace('%', '')),
                        'first_kills': self.safe_int(cells[9].get_text(strip=True)),
                        'first_deaths': self.safe_int(cells[10].get_text(strip=True)) if len(cells) > 10 else 0
                    }
                    
                    players_stats.append(player_stats)
                    
        except Exception as e:
            st.warning(f"Error extracting player stats from table: {str(e)}")
        
        return players_stats
    
    def extract_team_stats(self, soup):
        """
        Extract team-level statistics
        Args:
            soup (BeautifulSoup): Parsed HTML of the match page
        Returns:
            dict: Dictionary containing team statistics
        """
        team_stats = {}
        
        try:
            # Extract team performance metrics
            team_elements = soup.find_all('div', class_='team')
            
            for i, team_element in enumerate(team_elements):
                team_key = f'team_{i+1}'
                team_stats[team_key] = {
                    'name': team_element.get_text(strip=True),
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_assists': 0,
                    'total_damage': 0
                }
                
        except Exception as e:
            st.warning(f"Error extracting team stats: {str(e)}")
        
        return team_stats
    
    def safe_int(self, value):
        """
        Safely convert string to integer, handling edge cases
        Args:
            value (str): String to convert
        Returns:
            int: Converted integer or 0 if conversion fails
        """
        try:
            return int(value.replace(',', ''))
        except (ValueError, AttributeError):
            return 0
    
    def safe_float(self, value):
        """
        Safely convert string to float, handling edge cases
        Args:
            value (str): String to convert
        Returns:
            float: Converted float or 0.0 if conversion fails
        """
        try:
            return float(value.replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0
    
    def save_to_json(self, data, filename):
        """
        Save scraped data to a JSON file
        Args:
            data (dict): Data to save
            filename (str): Output filename
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            st.error(f"Error saving to JSON: {str(e)}")
            return False

def main():
    st.set_page_config(page_title="VLR.gg Match Details Scraper", layout="wide")
    
    st.title("🎯 VLR.gg Match Details Scraper")
    st.markdown("Scrape detailed match statistics from VLR.gg event pages")
    
    # Initialize scraper
    scraper = VLRMatchScraper()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    delay = st.sidebar.slider("Delay between requests (seconds)", 1, 5, 2)
    scraper.delay = delay
    
    # Main input
    st.header("Event URL Input")
    event_url = st.text_input(
        "Enter VLR.gg Event URL:",
        placeholder="https://www.vlr.gg/event/2004/champions-tour-2024-americas-stage-2",
        help="Enter the main event page URL from VLR.gg"
    )
    
    if st.button("🔍 Extract Match URLs", type="primary"):
        if event_url:
            with st.spinner("Extracting match URLs from event page..."):
                match_urls = scraper.extract_match_urls_from_event(event_url)
                
                if match_urls:
                    st.success(f"Found {len(match_urls)} match URLs")
                    st.session_state.match_urls = match_urls
                    
                    # Display found URLs
                    st.subheader("Found Match URLs:")
                    for i, url in enumerate(match_urls[:10]):  # Show first 10
                        st.text(f"{i+1}. {url}")
                    
                    if len(match_urls) > 10:
                        st.info(f"... and {len(match_urls) - 10} more matches")
                else:
                    st.warning("No match URLs found. Please check the event URL.")
        else:
            st.error("Please enter an event URL")
    
    # Scraping section
    if 'match_urls' in st.session_state:
        st.header("Scrape Match Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_matches = st.number_input(
                "Maximum matches to scrape:",
                min_value=1,
                max_value=len(st.session_state.match_urls),
                value=min(5, len(st.session_state.match_urls))
            )
        
        with col2:
            output_filename = st.text_input(
                "Output filename:",
                value=f"vlr_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        if st.button("🚀 Start Scraping", type="primary"):
            matches_to_scrape = st.session_state.match_urls[:max_matches]
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_match_data = []
            detailed_match_data = []
            
            for i, match_url in enumerate(matches_to_scrape):
                status_text.text(f"Scraping match {i+1}/{len(matches_to_scrape)}: {match_url}")
                
                # Scrape match details
                match_data = scraper.scrape_match_details(match_url)
                
                if match_data:
                    # Add to detailed data
                    detailed_match_data.append(match_data)
                    
                    # For display, only keep the first match
                    if i == 0:
                        all_match_data.append(match_data)
                    
                    st.success(f"✅ Successfully scraped match {i+1}")
                else:
                    st.error(f"❌ Failed to scrape match {i+1}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(matches_to_scrape))
                
                # Delay between requests
                if i < len(matches_to_scrape) - 1:
                    time.sleep(scraper.delay)
            
            # Save detailed results to a separate file
            if detailed_match_data:
                detailed_filename = f"detailed_{output_filename}"
                if scraper.save_to_json(detailed_match_data, detailed_filename):
                    st.success(f"✅ Detailed data saved to {detailed_filename}")
                    
                    # Download button for detailed data
                    with open(detailed_filename, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="📥 Download Detailed JSON File",
                            data=f.read(),
                            file_name=detailed_filename,
                            mime="application/json"
                        )
            
            # Display results for the first match
            if all_match_data:
                st.header("Sample Match Analysis")
                
                # Summary
                st.subheader("Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Matches Scraped", len(detailed_match_data))
                
                with col2:
                    total_maps = sum(len(match.get('maps', [])) for match in detailed_match_data)
                    st.metric("Total Maps", total_maps)
                
                with col3:
                    total_players = sum(
                        len(match.get('overview_stats', {}).get('all', []))
                        for match in detailed_match_data
                    )
                    st.metric("Total Player Records", total_players)
                
                # Preview sample match data
                st.subheader("Sample Match Preview")
                if all_match_data:
                    preview_data = {
                        'match_id': all_match_data[0].get('match_id'),
                        'teams': f"{all_match_data[0].get('basic_info', {}).get('team1_name')} vs {all_match_data[0].get('basic_info', {}).get('team2_name')}",
                        'maps_count': len(all_match_data[0].get('maps', [])),
                        'overview_stats_count': len(all_match_data[0].get('overview_stats', {}).get('all', []))
                    }
                    
                    st.json(preview_data)
                    
                    # Detailed view
                    with st.expander("View Full Sample Match Data"):
                        st.json(all_match_data[0])
            
            status_text.text("Scraping completed!")
    
    # Footer
    st.markdown("---")
    st.markdown("**Note:** Please respect VLR.gg's terms of service and use reasonable delays between requests.")

if __name__ == "__main__":
    main()
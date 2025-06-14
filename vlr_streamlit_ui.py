import streamlit as st
import pandas as pd
from datetime import datetime
import json
import time
import re
from urllib.parse import urlparse

# Import scrapers
from matches_scraper import MatchesScraper
from player_stats_scraper import PlayerStatsScraper
from maps_agents_scraper import MapsAgentsScraper
from match_details_scraper import VLRMatchScraper

def init_session_state():
    """Initialize session state variables"""
    if 'matches_data' not in st.session_state:
        st.session_state.matches_data = None
    if 'stats_data' not in st.session_state:
        st.session_state.stats_data = None
    if 'maps_agents_data' not in st.session_state:
        st.session_state.maps_agents_data = None
    if 'detailed_matches' not in st.session_state:
        st.session_state.detailed_matches = None

def display_header():
    """Display the app header"""
    st.title("🎮 VLR.gg Event Scraper")
    st.markdown("Simple and efficient VLR.gg tournament data extraction")
    st.markdown("""
    Three-step process:
    1. 🔍 Scrape: Extract data from VLR.gg event pages
    2. 👁️ Review: Confirm what data was scraped
    3. 💾 Save: Choose how to save your data
    """)

def display_url_input():
    """Display URL input section"""
    st.header("📝 Event URL Input")
    url = st.text_input(
        "VLR.gg Event URL:",
        placeholder="https://www.vlr.gg/event/1234/example-tournament",
        help="Enter the main event page URL from VLR.gg"
    )
    return url

def display_control_panel(url):
    """Display scraping control panel"""
    st.header("🔍 Step 1: Scrape Data")
    st.markdown("Select what to scrape:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scrape_matches = st.checkbox("Matches", value=True)
        scrape_stats = st.checkbox("Player Stats", value=True)
    
    with col2:
        scrape_maps_agents = st.checkbox("Maps & Agents", value=True)
        scrape_detailed_matches = st.checkbox("Detailed Matches", value=True)
    
    max_detailed_matches = st.number_input(
        "Max detailed matches to scrape:",
        min_value=1,
        max_value=50,
        value=5
    )
    
    return scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches

def display_progress():
    """Display progress section"""
    return st.empty()

def extract_event_id(url):
    """Extract event ID from VLR.gg URL"""
    try:
        # Extract event ID from URL pattern: /event/1234/...
        match = re.search(r'/event/(\d+)/', url)
        if match:
            return match.group(1)
        return None
    except Exception:
        return None

def perform_scraping(url, scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches, status_container):
    """Perform the scraping operation based on selected options"""
    
    def update_progress(message):
        status_container.text(message)
    
    try:
        # Initialize scrapers
        matches_scraper = MatchesScraper()
        stats_scraper = PlayerStatsScraper()
        maps_agents_scraper = MapsAgentsScraper()
        match_details_scraper = VLRMatchScraper()
        
        # Extract event ID from URL
        event_id = extract_event_id(url)
        if not event_id:
            st.error("Invalid event URL. Please check the URL format.")
            return
        
        # Scrape matches if selected
        if scrape_matches:
            update_progress("Scraping matches...")
            matches_data = matches_scraper.scrape_matches(url)
            if matches_data:
                st.session_state.matches_data = matches_data
                update_progress(f"✅ Scraped {len(matches_data.get('matches', []))} matches")
            else:
                update_progress("❌ Failed to scrape matches")
        
        # Scrape stats if selected
        if scrape_stats:
            update_progress("Scraping stats...")
            stats_data = stats_scraper.scrape_player_stats(url)
            if stats_data:
                st.session_state.stats_data = stats_data
                update_progress(f"✅ Scraped {len(stats_data.get('players', []))} player stats")
            else:
                update_progress("❌ Failed to scrape stats")
        
        # Scrape maps and agents if selected
        if scrape_maps_agents:
            update_progress("Scraping maps and agents...")
            maps_agents_data = maps_agents_scraper.scrape_maps_and_agents(url)
            if maps_agents_data:
                st.session_state.maps_agents_data = maps_agents_data
                update_progress("✅ Scraped maps and agents data")
            else:
                update_progress("❌ Failed to scrape maps and agents")
        
        # Scrape detailed matches if selected
        if scrape_detailed_matches and st.session_state.matches_data:
            update_progress("Scraping detailed matches...")
            match_urls = [match.get('match_url') for match in st.session_state.matches_data.get('matches', [])]
            match_urls = match_urls[:max_detailed_matches]
            
            detailed_matches = []
            for i, match_url in enumerate(match_urls):
                update_progress(f"Scraping detailed match {i+1}/{len(match_urls)}...")
                match_data = match_details_scraper.scrape_match_details(match_url)
                if match_data:
                    detailed_matches.append(match_data)
                    update_progress(f"✅ Scraped match {i+1}")
                else:
                    update_progress(f"❌ Failed to scrape match {i+1}")
                
                if i < len(match_urls) - 1:
                    time.sleep(2)
            
            if detailed_matches:
                st.session_state.detailed_matches = detailed_matches
                update_progress(f"✅ Scraped {len(detailed_matches)} detailed matches")
            else:
                update_progress("❌ Failed to scrape detailed matches")
        
        update_progress("Scraping completed!")
        
    except Exception as e:
        st.error(f"An error occurred during scraping: {str(e)}")
        update_progress("❌ Scraping failed")

def display_save_options():
    """Display options for saving scraped data"""
    st.header("💾 Step 3: Save Data")
    
    if not any([st.session_state.matches_data, st.session_state.stats_data, 
                st.session_state.maps_agents_data, st.session_state.detailed_matches]):
        st.warning("No data to save. Please scrape some data first.")
        return
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save matches data
    if st.session_state.matches_data:
        if st.button("Save Matches Data"):
            filename = f"matches_data_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.matches_data, f, indent=2)
            st.success(f"✅ Saved matches data to {filename}")
    
    # Save stats data
    if st.session_state.stats_data:
        if st.button("Save Player Stats Data"):
            filename = f"player_stats_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.stats_data, f, indent=2)
            st.success(f"✅ Saved player stats to {filename}")
    
    # Save maps and agents data
    if st.session_state.maps_agents_data:
        if st.button("Save Maps & Agents Data"):
            filename = f"maps_agents_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.maps_agents_data, f, indent=2)
            st.success(f"✅ Saved maps and agents data to {filename}")
    
    # Save detailed matches data
    if st.session_state.detailed_matches:
        if st.button("Save Detailed Matches Data"):
            filename = f"detailed_matches_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.detailed_matches, f, indent=2)
            st.success(f"✅ Saved detailed matches data to {filename}")

def main():
    """Main function to run the Streamlit app"""
    # Initialize session state
    init_session_state()
    
    # Display header
    display_header()
    
    # Get URL input
    url = display_url_input()
    
    if url:
        # Display control panel and get scraping options
        scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches = display_control_panel(url)
        
        # Create progress container
        status_container = display_progress()
        
        # Start scraping button
        if st.button("Start Scraping", type="primary"):
            perform_scraping(
                url, 
                scrape_matches, 
                scrape_stats, 
                scrape_maps_agents, 
                scrape_detailed_matches, 
                max_detailed_matches,
                status_container
            )
        
        # Display save options
        display_save_options()

if __name__ == "__main__":
    main()

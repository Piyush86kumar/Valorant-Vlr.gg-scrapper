#!/usr/bin/env python3
"""
Test script for the Detailed Match Scraper
Verifies that the scraper works correctly with Chrome and ChromeDriver
"""

from detailed_match_scraper import DetailedMatchScraper
import json
from datetime import datetime

def main():
    # Initialize the scraper
    scraper = DetailedMatchScraper()
    
    # Test URL - MIBR vs LEVIATÁN match
    test_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    
    print("🔍 Testing Detailed Match Scraper with Chrome")
    print("=" * 50)
    print(f"🎯 Test URL: {test_url}")
    
    try:
        # Scrape the match
        match_data = scraper.scrape_match(test_url)
        
        # Print basic match info
        print("\n✅ Match scraped successfully!")
        print(f"📊 Match ID: {match_data.get('match_id')}")
        print(f"🏟️ Teams: {match_data.get('team1_name')} vs {match_data.get('team2_name')}")
        print(f"📅 Date: {match_data.get('match_date')}")
        print(f"🎮 Format: {match_data.get('format')}")
        print(f"🔄 Patch: {match_data.get('patch')}")
        
        # Print map details
        print("\n🗺️ Maps played:")
        for map_data in match_data.get('maps', []):
            print(f"\n  Map: {map_data.get('map_name')}")
            print(f"  Score: {map_data.get('team1_score')} - {map_data.get('team2_score')}")
            print(f"  Picked by: {map_data.get('pick_team')}")
            
            # Print player stats for first player of each team
            print("\n  Player Stats (first player from each team):")
            for player in map_data.get('player_stats', [])[:2]:
                print(f"    {player.get('player_name')}:")
                print(f"      K/D/A: {player.get('k', '-')}/{player.get('d', '-')}/{player.get('a', '-')}")
                print(f"      ACS: {player.get('acs', '-')}")
        
        # Save the data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'test_detailed_match_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(match_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Full match data saved to '{filename}'")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

def clean_team_name(team_text):
    """Clean team name by removing ID and extra text"""
    # Remove team ID in brackets
    team_text = re.sub(r'\[\d+\]', '', team_text)
    return team_text.strip()

def clean_map_name(map_text):
    """Clean map name by removing PICK and timestamps"""
    # Remove PICK and timestamps
    map_text = re.sub(r'PICK.*$', '', map_text)
    map_text = re.sub(r'\d+:\d+:\d+', '', map_text)
    return map_text.strip()

def analyze_match_page_structure(url):
    """
    Analyze the HTML structure of a VLR.gg match details page
    Args:
        url (str): URL of the match page to analyze
    Returns:
        dict: Dictionary containing the page structure analysis
    """
    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the page
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Initialize structure dictionary
        structure = {
            'match_header': {},
            'maps_data': [],
            'player_stats': {},
            'team_stats': {}
        }
        
        # Analyze match header
        header = soup.find('div', class_='match-header')
        if header:
            team_elements = header.find_all('div', class_='match-header-link-name')
            teams = [clean_team_name(team.get_text(strip=True)) for team in team_elements]
            
            score_element = header.find('div', class_='match-header-vs-score')
            score_text = score_element.get_text(strip=True) if score_element else None
            
            # Clean up score text
            if score_text:
                score_text = re.sub(r'final', '', score_text)
                score_text = re.sub(r'vs\.', '', score_text)
                score_text = score_text.strip()
            
            structure['match_header'] = {
                'teams': teams,
                'score': score_text,
                'event': header.find('div', class_='match-header-event').get_text(strip=True) if header.find('div', class_='match-header-event') else None
            }
        
        # Analyze maps data
        maps_sections = soup.find_all('div', class_='vm-stats-game')
        for map_section in maps_sections:
            map_name_element = map_section.find('div', class_='map')
            map_name = clean_map_name(map_name_element.get_text(strip=True)) if map_name_element else None
            
            map_data = {
                'map_name': map_name,
                'scores': [score.get_text(strip=True) for score in map_section.find_all('div', class_='score')],
                'stats_tables': []
            }
            
            # Analyze stats tables
            tables = map_section.find_all('table', class_='vm-stats-game-table')
            for table in tables:
                table_data = {
                    'headers': [th.get_text(strip=True) for th in table.find_all('th')],
                    'rows': len(table.find_all('tr')) - 1,  # Subtract header row
                    'player_stats': []
                }
                
                # Extract player stats
                rows = table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cells = row.find_all('td')
                    if cells:
                        player_stats = {
                            'player_name': cells[0].get_text(strip=True) if cells else None,
                            'agent': cells[0].find('img')['alt'] if cells[0].find('img') else None,
                            'stats': {}
                        }
                        
                        # Extract stats from remaining cells
                        for i, cell in enumerate(cells[1:], 1):
                            if i < len(table_data['headers']):
                                stat_name = table_data['headers'][i]
                                player_stats['stats'][stat_name] = cell.get_text(strip=True)
                        
                        table_data['player_stats'].append(player_stats)
                
                map_data['stats_tables'].append(table_data)
            
            structure['maps_data'].append(map_data)
        
        # Save the structure to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'match_page_structure_{timestamp}.json'
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Structure analysis saved to {filename}")
        return structure
        
    except Exception as e:
        print(f"❌ Error analyzing match page: {str(e)}")
        return None

if __name__ == "__main__":
    # Test URL
    test_url = "https://www.vlr.gg/429381/bbl-esports-vs-giantx-champions-tour-2025-emea-kickoff-ur1"
    
    print("🔍 Analyzing VLR.gg Match Page Structure")
    print("=" * 40)
    
    structure = analyze_match_page_structure(test_url)
    
    if structure:
        print("\n📊 Structure Analysis Summary:")
        print(f"   🏆 Teams: {structure['match_header']['teams']}")
        print(f"   📊 Score: {structure['match_header']['score']}")
        print(f"   🎮 Maps: {len(structure['maps_data'])}")
        
        # Print map details
        for i, map_data in enumerate(structure['maps_data'], 1):
            print(f"\n   Map {i}: {map_data['map_name']}")
            print(f"   Scores: {map_data['scores']}")
            print(f"   Stats Tables: {len(map_data['stats_tables'])}")
            
            # Print player stats summary for each table
            for j, table in enumerate(map_data['stats_tables'], 1):
                print(f"\n      Table {j}:")
                print(f"      Headers: {table['headers']}")
                print(f"      Players: {len(table['player_stats'])}")
                
                # Print first player's stats as example
                if table['player_stats']:
                    first_player = table['player_stats'][0]
                    print(f"      Sample Player: {first_player['player_name']} ({first_player['agent']})")
                    print(f"      Sample Stats: {first_player['stats']}") 
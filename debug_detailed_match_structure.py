import requests
from bs4 import BeautifulSoup
import json
import time

def analyze_match_page_structure(url: str):
    """Analyze the structure of a detailed match page to help with scraping."""
    print(f"\nAnalyzing match page: {url}")
    
    # Set up headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Get the page content
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Save the full HTML for reference
        with open('debug_match_full.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Saved full HTML to debug_match_full.html")
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Analyze match header
        print("\n1. Match Header Analysis:")
        header = soup.find('div', class_='match-header')
        if header:
            print("Found match header with classes:", header.get('class', []))
            # Print all text elements in header
            for element in header.find_all(['div', 'span', 'a']):
                if element.text.strip():
                    print(f"- {element.name}: {element.text.strip()}")
        else:
            print("No match header found")
            
        # 2. Analyze map containers
        print("\n2. Map Containers Analysis:")
        map_containers = soup.find_all('div', class_='vm-stats-game')
        print(f"Found {len(map_containers)} map containers")
        
        for container in map_containers:
            game_id = container.get('data-game-id', 'unknown')
            print(f"\nMap Container (game_id: {game_id}):")
            
            # Get map header
            header = container.find('div', class_='vm-stats-game-header')
            if header:
                print("Header content:", header.text.strip())
            
            # Get map name and score
            map_name = container.find('div', class_='map')
            if map_name:
                print("Map name:", map_name.text.strip())
            
            # Get team scores
            scores = container.find_all('div', class_='score')
            if scores:
                print("Scores:", [score.text.strip() for score in scores])
            
            # Get stats tables
            stats_tables = container.find_all('table')
            print(f"Found {len(stats_tables)} stats tables in this container")
            
            for table in stats_tables:
                print("\nTable structure:")
                # Get headers
                headers = table.find_all('th')
                if headers:
                    print("Headers:", [h.text.strip() for h in headers])
                
                # Get first row
                first_row = table.find('tr')
                if first_row:
                    cells = first_row.find_all(['td', 'th'])
                    print("First row:", [cell.text.strip() for cell in cells])
        
        # 3. Analyze player lineups
        print("\n3. Player Lineups Analysis:")
        player_links = soup.find_all('a', class_='team-player')
        print(f"Found {len(player_links)} player links")
        
        # Group players by team
        team_players = {}
        for link in player_links[:10]:  # Show first 10 players
            player_name = link.text.strip()
            team_name = "Unknown"
            team_elem = link.find_parent('div', class_='team')
            if team_elem:
                team_name = team_elem.find('div', class_='team-name')
                if team_name:
                    team_name = team_name.text.strip()
            
            if team_name not in team_players:
                team_players[team_name] = []
            team_players[team_name].append(player_name)
        
        for team, players in team_players.items():
            print(f"\n{team}:")
            for player in players:
                print(f"- {player}")
        
        # 4. Analyze dynamic data structure
        print("\n4. Dynamic Data Structure Analysis:")
        # Look for data attributes that might contain match info
        data_elements = soup.find_all(lambda tag: any(attr for attr in tag.attrs if attr.startswith('data-')))
        print("\nFound elements with data attributes:")
        for elem in data_elements[:5]:  # Show first 5 elements
            print(f"\nElement: {elem.name}")
            for attr, value in elem.attrs.items():
                if attr.startswith('data-'):
                    print(f"- {attr}: {value}")
        
        print("\nAnalysis complete!")
        
    except Exception as e:
        print(f"Error analyzing page: {str(e)}")

if __name__ == "__main__":
    # Example match URL
    match_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    analyze_match_page_structure(match_url) 
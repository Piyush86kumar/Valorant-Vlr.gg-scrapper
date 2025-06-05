#!/usr/bin/env python3
"""
Debug script to examine the actual HTML structure of VLR.gg player stats page
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_player_stats_structure():
    """Debug the HTML structure of VLR.gg player stats page"""
    
    url = "https://www.vlr.gg/event/stats/2095/champions-tour-2024-americas-stage-2"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging player stats structure for: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for stats tables
        print(f"\n🔍 Searching for stats tables...")
        
        # Method 1: Look for wf-table-inset
        wf_tables = soup.find_all('table', class_='wf-table-inset')
        print(f"📊 table.wf-table-inset found: {len(wf_tables)}")
        
        if wf_tables:
            print(f"   🔍 Analyzing first table...")
            first_table = wf_tables[0]
            
            # Check headers
            headers = first_table.find_all('th')
            print(f"   📋 Headers found: {len(headers)}")
            for i, header in enumerate(headers):
                print(f"      {i}: {header.get_text(strip=True)}")
            
            # Check first few data rows
            rows = first_table.find_all('tr')
            print(f"   📊 Total rows: {len(rows)}")
            
            if len(rows) > 1:
                print(f"   🔍 Analyzing first data row...")
                first_row = rows[1]  # Skip header
                cells = first_row.find_all('td')
                print(f"      📊 Cells in first row: {len(cells)}")
                
                for i, cell in enumerate(cells):
                    cell_text = cell.get_text(strip=True)
                    print(f"         Cell {i}: '{cell_text}' (first 50 chars)")
                    
                    # Check for player/team links
                    links = cell.find_all('a')
                    if links:
                        for link in links:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)
                            print(f"            Link: '{link_text}' -> {href}")
        
        # Method 2: Look for any tables
        all_tables = soup.find_all('table')
        print(f"\n📊 Total tables found: {len(all_tables)}")
        
        for i, table in enumerate(all_tables):
            classes = table.get('class', [])
            print(f"   Table {i}: classes = {classes}")
            
            # Check if this looks like a stats table
            rows = table.find_all('tr')
            if len(rows) > 1:
                first_row = rows[0]
                headers = first_row.find_all(['th', 'td'])
                header_text = [h.get_text(strip=True) for h in headers]
                print(f"      Headers: {header_text}")
        
        # Method 3: Look for specific stat-related elements
        print(f"\n🔍 Looking for stat-related elements...")
        
        # Look for elements with 'stat' in class name
        stat_elements = soup.find_all(attrs={'class': re.compile(r'stat', re.I)})
        stat_classes = set()
        for elem in stat_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'stat' in cls.lower():
                    stat_classes.add(cls)
        
        print(f"   🏷️ Classes containing 'stat': {sorted(stat_classes)}")
        
        # Look for player-related elements
        player_elements = soup.find_all(attrs={'class': re.compile(r'player', re.I)})
        player_classes = set()
        for elem in player_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'player' in cls.lower():
                    player_classes.add(cls)
        
        print(f"   🏷️ Classes containing 'player': {sorted(player_classes)}")
        
        # Save a sample of the HTML for manual inspection
        with open('debug_player_stats_sample.html', 'w', encoding='utf-8') as f:
            # Save first 100KB of HTML
            f.write(str(soup)[:100000])
        
        print(f"\n💾 HTML sample saved to 'debug_player_stats_sample.html' (first 100KB)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_player_stats_structure()

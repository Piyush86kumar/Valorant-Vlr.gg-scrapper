#!/usr/bin/env python3
"""
Debug script to examine the actual HTML structure of VLR.gg agents page
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_agents_page_structure():
    """Debug the HTML structure of VLR.gg agents page"""
    
    url = "https://www.vlr.gg/event/agents/2095/champions-tour-2024-americas-stage-2"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging agents page structure for: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for all tables
        print(f"\n🔍 Searching for tables...")
        
        all_tables = soup.find_all('table')
        print(f"📊 Total tables found: {len(all_tables)}")
        
        for i, table in enumerate(all_tables):
            classes = table.get('class', [])
            print(f"\n   Table {i+1}: classes = {classes}")
            
            # Check headers
            headers = table.find_all('th')
            if headers:
                header_texts = [h.get_text(strip=True) for h in headers]
                print(f"      Headers: {header_texts}")
                
                # Check first few data rows
                rows = table.find_all('tr')
                if len(rows) > 1:
                    print(f"      Total rows: {len(rows)} (including header)")
                    
                    # Show first data row
                    if len(rows) > 1:
                        first_row = rows[1]
                        cells = first_row.find_all('td')
                        if cells:
                            print(f"      First row cells: {len(cells)}")
                            for j, cell in enumerate(cells[:8]):  # Show first 8 cells
                                cell_text = cell.get_text(strip=True)
                                print(f"         Cell {j}: '{cell_text}' (first 30 chars)")
                    
                    # Show second data row if exists
                    if len(rows) > 2:
                        second_row = rows[2]
                        cells = second_row.find_all('td')
                        if cells:
                            print(f"      Second row cells: {len(cells)}")
                            for j, cell in enumerate(cells[:4]):  # Show first 4 cells
                                cell_text = cell.get_text(strip=True)
                                print(f"         Cell {j}: '{cell_text}' (first 30 chars)")
        
        # Look for specific patterns
        print(f"\n🔍 Looking for specific patterns...")
        
        # Look for map-related elements
        map_elements = soup.find_all(attrs={'class': re.compile(r'map', re.I)})
        map_classes = set()
        for elem in map_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'map' in cls.lower():
                    map_classes.add(cls)
        
        print(f"   🗺️ Classes containing 'map': {sorted(map_classes)}")
        
        # Look for agent-related elements
        agent_elements = soup.find_all(attrs={'class': re.compile(r'agent', re.I)})
        agent_classes = set()
        for elem in agent_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'agent' in cls.lower():
                    agent_classes.add(cls)
        
        print(f"   🎭 Classes containing 'agent': {sorted(agent_classes)}")
        
        # Save a sample of the HTML for manual inspection
        with open('debug_agents_page_sample.html', 'w', encoding='utf-8') as f:
            # Save first 100KB of HTML
            f.write(str(soup)[:100000])
        
        print(f"\n💾 HTML sample saved to 'debug_agents_page_sample.html' (first 100KB)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_agents_page_structure()

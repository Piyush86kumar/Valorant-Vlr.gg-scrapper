#!/usr/bin/env python3
"""
Debug script to examine the actual HTML structure of VLR.gg match page
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_match_page_structure():
    """Debug the HTML structure of VLR.gg match page"""
    
    url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging match page structure for: {url}")
    print("=" * 70)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Look for team names in title
        if soup.title:
            title_text = soup.title.string
            vs_match = re.search(r'([^/]+?)\s+vs\s+([^/]+?)(?:\s|/)', title_text)
            if vs_match:
                print(f"🏟️ Teams from title: '{vs_match.group(1)}' vs '{vs_match.group(2)}'")
        
        # Look for match header elements
        print(f"\n🔍 Searching for match header elements...")
        
        # Check various selectors for team names
        team_selectors = [
            'div.match-header-link',
            'a.match-header-link',
            'div.match-header-link-name',
            'div.text-of',
            'span.text-of',
            'div.wf-title-med',
            'div.match-header-vs'
        ]
        
        for selector in team_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n   Selector '{selector}' found {len(elements)} elements:")
                for i, elem in enumerate(elements[:5]):  # Show first 5
                    text = elem.get_text(strip=True)
                    print(f"      {i+1}: '{text}' (first 50 chars)")
        
        # Look for score elements
        print(f"\n🔍 Searching for score elements...")
        
        score_selectors = [
            'div.match-header-vs-score',
            'div.js-spoiler',
            'span.js-spoiler',
            'div.score'
        ]
        
        for selector in score_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n   Selector '{selector}' found {len(elements)} elements:")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text = elem.get_text(strip=True)
                    print(f"      {i+1}: '{text}'")
        
        # Look for map elements
        print(f"\n🔍 Searching for map elements...")
        
        map_selectors = [
            'div.vm-stats-game',
            'div.map',
            'div.vlr-rounds-row-col'
        ]
        
        for selector in map_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\n   Selector '{selector}' found {len(elements)} elements:")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    text = elem.get_text(strip=True)
                    print(f"      {i+1}: '{text}' (first 100 chars)")
        
        # Save a sample of the HTML for manual inspection
        with open('debug_match_page_sample.html', 'w', encoding='utf-8') as f:
            # Save first 200KB of HTML
            f.write(str(soup)[:200000])
        
        print(f"\n💾 HTML sample saved to 'debug_match_page_sample.html' (first 200KB)")
        
        # Look for specific patterns in the HTML
        print(f"\n🔍 Looking for specific patterns...")
        
        # Search for team-related classes
        team_classes = set()
        for elem in soup.find_all(attrs={'class': True}):
            classes = elem.get('class', [])
            for cls in classes:
                if any(keyword in cls.lower() for keyword in ['team', 'match', 'header', 'vs']):
                    team_classes.add(cls)
        
        print(f"   🏟️ Team-related classes: {sorted(list(team_classes))[:10]}")  # Show first 10
        
        # Search for elements containing "vs"
        vs_elements = soup.find_all(string=re.compile(r'vs', re.I))
        print(f"   ⚔️ Elements containing 'vs': {len(vs_elements)}")
        if vs_elements:
            for i, elem in enumerate(vs_elements[:3]):
                print(f"      {i+1}: '{str(elem).strip()}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_match_page_structure()

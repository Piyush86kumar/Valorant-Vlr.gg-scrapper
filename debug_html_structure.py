#!/usr/bin/env python3
"""
Debug script to examine the actual HTML structure of VLR.gg matches page
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_html_structure():
    """Debug the HTML structure of VLR.gg matches page"""
    
    url = "https://www.vlr.gg/event/matches/2095/champions-tour-2024-americas-stage-2"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"🔍 Debugging HTML structure for: {url}")
    print("=" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"✅ Successfully fetched page (Status: {response.status_code})")
        print(f"📄 Page title: {soup.title.string if soup.title else 'No title'}")
        
        # Check for different possible match container structures
        print(f"\n🔍 Searching for match containers...")
        
        # Method 1: Look for vm-date structure (from debug file)
        vm_dates = soup.select("div.vm-date")
        print(f"📅 div.vm-date containers: {len(vm_dates)}")
        
        if vm_dates:
            print(f"   Found vm-date structure! Analyzing first container...")
            first_date = vm_dates[0]
            
            # Check for date label
            date_label = first_date.find('div', class_='vm-date-label')
            print(f"   📅 Date label: {date_label.get_text(strip=True) if date_label else 'Not found'}")
            
            # Check for matches
            vm_matches = first_date.find_all('a', class_='vm-match')
            print(f"   🏟️ vm-match elements in first date: {len(vm_matches)}")
            
            if vm_matches:
                print(f"   🔍 Analyzing first match...")
                first_match = vm_matches[0]
                
                # Check team structure
                team_elems = first_match.select('div.vm-t')
                print(f"      👥 Team containers (div.vm-t): {len(team_elems)}")
                
                if team_elems:
                    for i, team in enumerate(team_elems):
                        team_name = team.find('div', class_='vm-t-name')
                        print(f"         Team {i+1}: {team_name.get_text(strip=True) if team_name else 'Not found'}")
                
                # Check score
                score_elem = first_match.find('div', class_='vm-score')
                print(f"      📊 Score: {score_elem.get_text(strip=True) if score_elem else 'Not found'}")
                
                # Check time
                time_elem = first_match.find('div', class_='vm-time')
                print(f"      ⏰ Time: {time_elem.get_text(strip=True) if time_elem else 'Not found'}")
                
                # Check status
                status_elem = first_match.find('div', class_='vm-status')
                print(f"      📍 Status: {status_elem.get_text(strip=True) if status_elem else 'Not found'}")
                
                # Check week/stage info
                stats_container = first_match.find('div', class_='vm-stats-container')
                print(f"      📈 Stats container: {stats_container.get_text(strip=True) if stats_container else 'Not found'}")
        
        # Method 2: Look for wf-module-item structure (current fallback)
        wf_items = soup.find_all('a', class_='wf-module-item')
        print(f"\n📦 a.wf-module-item containers: {len(wf_items)}")
        
        if wf_items:
            print(f"   🔍 Analyzing first wf-module-item...")
            first_item = wf_items[0]
            print(f"      🔗 href: {first_item.get('href', 'No href')}")
            print(f"      📝 Text content (first 100 chars): {first_item.get_text(strip=True)[:100]}...")
            
            # Look for team elements
            team_elements = first_item.find_all(['div', 'span'], class_=re.compile(r'team.*name|match.*team'))
            print(f"      👥 Team elements found: {len(team_elements)}")
            for i, elem in enumerate(team_elements[:4]):  # Show first 4
                print(f"         Team element {i+1}: {elem.get_text(strip=True)}")
        
        # Method 3: Look for any other match-related structures
        print(f"\n🔍 Other potential match structures...")
        
        # Look for any elements with 'match' in class name
        match_elements = soup.find_all(attrs={'class': re.compile(r'match', re.I)})
        match_classes = set()
        for elem in match_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if 'match' in cls.lower():
                    match_classes.add(cls)
        
        print(f"   🏷️ Classes containing 'match': {sorted(match_classes)}")
        
        # Look for any elements with 'vm-' prefix
        vm_elements = soup.find_all(attrs={'class': re.compile(r'vm-')})
        vm_classes = set()
        for elem in vm_elements:
            classes = elem.get('class', [])
            for cls in classes:
                if cls.startswith('vm-'):
                    vm_classes.add(cls)
        
        print(f"   🏷️ Classes starting with 'vm-': {sorted(vm_classes)}")
        
        # Save a sample of the HTML for manual inspection
        with open('debug_html_sample.html', 'w', encoding='utf-8') as f:
            # Save first 50KB of HTML
            f.write(str(soup)[:50000])
        
        print(f"\n💾 HTML sample saved to 'debug_html_sample.html' (first 50KB)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_html_structure()

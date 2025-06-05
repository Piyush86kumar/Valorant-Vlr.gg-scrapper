#!/usr/bin/env python3
"""
Comprehensive debug script for VLR.gg detailed match pages
Analyzes the actual HTML structure and data extraction issues
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

class DetailedMatchDebugger:
    """Debug detailed match page structure and data extraction"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def debug_match_page(self, match_url: str):
        """Comprehensive debug of a match page"""
        print(f"🔍 DEBUGGING MATCH PAGE")
        print("=" * 80)
        print(f"🎯 URL: {match_url}")
        
        try:
            response = self.session.get(match_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            print(f"✅ Page fetched successfully (Status: {response.status_code})")
            print(f"📄 Page size: {len(response.text)} characters")
            
            # Extract and save HTML for manual inspection
            with open('debug_match_full.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print(f"💾 Full HTML saved to 'debug_match_full.html'")
            
            # Debug sections
            self._debug_page_title(soup)
            self._debug_team_extraction(soup)
            self._debug_score_extraction(soup)
            self._debug_match_header(soup)
            self._debug_match_details(soup)
            self._debug_map_data(soup)
            self._debug_player_data(soup)
            self._debug_all_classes(soup)
            
            return soup
            
        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None
    
    def _debug_page_title(self, soup):
        """Debug page title extraction"""
        print(f"\n📄 PAGE TITLE DEBUG")
        print("-" * 40)
        
        title = soup.find('title')
        if title:
            title_text = title.string
            print(f"🏷️ Full title: '{title_text}'")
            
            # Try different patterns for team extraction
            patterns = [
                r'([^|/]+?)\s+vs\.?\s+([^|/]+?)(?:\s*\||$)',
                r'([^-]+?)\s+vs\.?\s+([^-]+?)(?:\s*-|$)',
                r'([^:]+?)\s+vs\.?\s+([^:]+?)(?:\s*:|$)'
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, title_text, re.IGNORECASE)
                if match:
                    print(f"✅ Pattern {i+1} matched: '{match.group(1).strip()}' vs '{match.group(2).strip()}'")
                else:
                    print(f"❌ Pattern {i+1} failed")
        else:
            print("❌ No title found")
    
    def _debug_team_extraction(self, soup):
        """Debug team name extraction"""
        print(f"\n🏟️ TEAM EXTRACTION DEBUG")
        print("-" * 40)
        
        # Try multiple selectors
        selectors = [
            'div.wf-title-med',
            'div.match-header-link div.wf-title-med',
            'a.match-header-link div.wf-title-med',
            'div.match-header-link-name',
            'div.text-of',
            'span.text-of',
            'div.match-header-vs div.text-of',
            'div.match-header-link .text-of'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            print(f"🔍 Selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:5]):  # Show first 5
                text = elem.get_text(strip=True)
                print(f"   {i+1}: '{text}'")
    
    def _debug_score_extraction(self, soup):
        """Debug score extraction"""
        print(f"\n📊 SCORE EXTRACTION DEBUG")
        print("-" * 40)
        
        # Try multiple selectors for scores
        selectors = [
            'div.js-spoiler',
            'span.js-spoiler',
            'div.match-header-vs-score',
            'div.score',
            'span.score'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            print(f"🔍 Selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:3]):  # Show first 3
                text = elem.get_text(strip=True)
                print(f"   {i+1}: '{text}'")
    
    def _debug_match_header(self, soup):
        """Debug match header information"""
        print(f"\n📋 MATCH HEADER DEBUG")
        print("-" * 40)
        
        # Look for match header container
        header_selectors = [
            'div.match-header',
            'div.match-header-super',
            'div.vlr-rounds-header',
            'div.match-header-event'
        ]
        
        for selector in header_selectors:
            elements = soup.select(selector)
            print(f"🔍 Header selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:2]):
                text = elem.get_text(strip=True)[:100]  # First 100 chars
                print(f"   {i+1}: '{text}...'")
    
    def _debug_match_details(self, soup):
        """Debug match details like date, time, format"""
        print(f"\n⏰ MATCH DETAILS DEBUG")
        print("-" * 40)
        
        # Look for date/time elements
        time_selectors = [
            'div.moment-tz-convert',
            'div.match-header-date',
            'span.moment-tz-convert',
            'div.vlr-rounds-header-date'
        ]
        
        for selector in time_selectors:
            elements = soup.select(selector)
            print(f"🔍 Time selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:2]):
                text = elem.get_text(strip=True)
                attrs = elem.attrs
                print(f"   {i+1}: '{text}' | Attrs: {attrs}")
    
    def _debug_map_data(self, soup):
        """Debug map data extraction"""
        print(f"\n🗺️ MAP DATA DEBUG")
        print("-" * 40)
        
        # Look for map containers
        map_selectors = [
            'div.vm-stats-game',
            'div.vlr-rounds-row',
            'div.map',
            'div.vlr-rounds-row-col'
        ]
        
        for selector in map_selectors:
            elements = soup.select(selector)
            print(f"🔍 Map selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:3]):
                text = elem.get_text(strip=True)[:150]  # First 150 chars
                print(f"   {i+1}: '{text}...'")
    
    def _debug_player_data(self, soup):
        """Debug player lineup extraction"""
        print(f"\n👥 PLAYER DATA DEBUG")
        print("-" * 40)
        
        # Look for player containers
        player_selectors = [
            'div.vm-stats-game-players',
            'div.vlr-rounds-row-players',
            'div.player',
            'span.player-name',
            'div.text-of'
        ]
        
        for selector in player_selectors:
            elements = soup.select(selector)
            print(f"🔍 Player selector '{selector}': {len(elements)} elements")
            for i, elem in enumerate(elements[:5]):
                text = elem.get_text(strip=True)
                print(f"   {i+1}: '{text}'")
    
    def _debug_all_classes(self, soup):
        """Debug all CSS classes to find relevant ones"""
        print(f"\n🎨 CSS CLASSES DEBUG")
        print("-" * 40)
        
        # Collect all unique classes
        all_classes = set()
        for elem in soup.find_all(attrs={'class': True}):
            classes = elem.get('class', [])
            for cls in classes:
                all_classes.add(cls)
        
        # Filter relevant classes
        relevant_keywords = ['match', 'team', 'score', 'player', 'map', 'header', 'vs', 'game', 'round']
        relevant_classes = []
        
        for cls in all_classes:
            if any(keyword in cls.lower() for keyword in relevant_keywords):
                relevant_classes.append(cls)
        
        print(f"📊 Total classes found: {len(all_classes)}")
        print(f"🎯 Relevant classes ({len(relevant_classes)}):")
        for cls in sorted(relevant_classes)[:20]:  # Show first 20
            print(f"   • {cls}")
    
    def test_multiple_matches(self, match_urls):
        """Test multiple match URLs to find patterns"""
        print(f"\n🔄 TESTING MULTIPLE MATCHES")
        print("=" * 80)
        
        results = []
        
        for i, url in enumerate(match_urls):
            print(f"\n🎯 Match {i+1}: {url}")
            print("-" * 60)
            
            try:
                response = self.session.get(url, timeout=15)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Quick extraction test
                result = {
                    'url': url,
                    'status': response.status_code,
                    'title': soup.find('title').string if soup.find('title') else 'No title',
                    'teams_found': len(soup.select('div.wf-title-med')),
                    'scores_found': len(soup.select('div.js-spoiler')),
                    'maps_found': len(soup.select('div.vm-stats-game'))
                }
                
                results.append(result)
                
                print(f"   ✅ Status: {result['status']}")
                print(f"   📄 Title: {result['title'][:60]}...")
                print(f"   🏟️ Teams found: {result['teams_found']}")
                print(f"   📊 Scores found: {result['scores_found']}")
                print(f"   🗺️ Maps found: {result['maps_found']}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({'url': url, 'error': str(e)})
        
        return results

def main():
    """Main debug function"""
    debugger = DetailedMatchDebugger()
    
    # Test URLs - mix of different match types
    test_urls = [
        "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1",
        "https://www.vlr.gg/353178/g2-esports-vs-cloud9-champions-tour-2024-americas-stage-2-w1",
        "https://www.vlr.gg/350000/sentinels-vs-100-thieves-champions-tour-2024-americas-stage-1",
    ]
    
    print("🎮 VLR.gg DETAILED MATCH COMPREHENSIVE DEBUG")
    print("=" * 80)
    
    # Debug first match in detail
    print(f"🔍 DETAILED DEBUG OF FIRST MATCH")
    soup = debugger.debug_match_page(test_urls[0])
    
    if soup:
        # Test multiple matches for patterns
        print(f"\n🔄 PATTERN ANALYSIS ACROSS MULTIPLE MATCHES")
        results = debugger.test_multiple_matches(test_urls[:2])  # Test first 2
        
        # Summary
        print(f"\n📊 DEBUG SUMMARY")
        print("=" * 80)
        print(f"✅ Analysis complete!")
        print(f"📄 Full HTML saved for manual inspection")
        print(f"🎯 Key findings will help improve the scraper")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        print(f"1. 🔍 Check 'debug_match_full.html' for actual page structure")
        print(f"2. 🎯 Look for alternative selectors in CSS classes debug")
        print(f"3. 📊 Verify score format and location")
        print(f"4. 🗺️ Check if map data is in different containers")
        print(f"5. 👥 Verify player data structure")

if __name__ == "__main__":
    main()

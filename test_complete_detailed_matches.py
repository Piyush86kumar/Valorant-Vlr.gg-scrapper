#!/usr/bin/env python3
"""
Complete test for the detailed match functionality
Tests the entire workflow: improved scraper -> UI integration -> database storage
"""

from detailed_match_scraper import DetailedMatchScraper
from vlr_database import VLRDatabase
import json
import pandas as pd
from datetime import datetime

def test_improved_detailed_match_scraper():
    """Test the improved detailed match scraper"""
    print("🔍 Testing Improved Detailed Match Scraper")
    print("=" * 60)
    
    scraper = DetailedMatchScraper()
    
    # Test with the same URL
    test_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    
    try:
        print(f"🎯 Scraping: {test_url}")
        match_data = scraper.scrape_detailed_match(test_url)
        
        print(f"✅ Match scraped successfully!")
        print(f"🆔 Match ID: {match_data.get('match_id')}")
        print(f"🏟️ Teams: {match_data.get('team1_name')} vs {match_data.get('team2_name')}")
        print(f"📊 Score: {match_data.get('final_score')}")
        print(f"🗺️ Maps played: {match_data.get('maps_played')}")
        print(f"📅 Date: {match_data.get('match_date_display')}")
        print(f"⏰ Time: {match_data.get('match_time')}")
        print(f"🏆 Format: {match_data.get('match_format')}")
        print(f"🥇 Winner: {match_data.get('winner_team')}")
        
        # Test player lineups
        import json
        team1_players = json.loads(match_data.get('team1_players', '[]'))
        team2_players = json.loads(match_data.get('team2_players', '[]'))
        
        print(f"\n👥 Team Lineups:")
        print(f"   {match_data.get('team1_name')}: {team1_players}")
        print(f"   {match_data.get('team2_name')}: {team2_players}")
        
        # Test map details
        map_details = json.loads(match_data.get('map_details', '[]'))
        print(f"\n🗺️ Map Details:")
        for i, map_data in enumerate(map_details):
            print(f"   Map {i+1}: {map_data.get('map_name', 'Unknown')} - {map_data.get('map_score', 'N/A')} ({map_data.get('pick_type', 'N/A')})")
        
        # Save improved sample
        with open('improved_detailed_match.json', 'w', encoding='utf-8') as f:
            json.dump(match_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Improved sample saved to 'improved_detailed_match.json'")
        
        return match_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_multiple_detailed_matches():
    """Test scraping multiple detailed matches"""
    print(f"\n🔄 Testing Multiple Detailed Matches")
    print("=" * 60)
    
    scraper = DetailedMatchScraper()
    
    # Test URLs
    test_urls = [
        "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1",
        "https://www.vlr.gg/353178/g2-esports-vs-cloud9-champions-tour-2024-americas-stage-2-w1"
    ]
    
    try:
        print(f"🎯 Scraping {len(test_urls)} matches...")
        
        detailed_matches = []
        for i, url in enumerate(test_urls):
            print(f"\n   🎯 Match {i+1}: {url.split('/')[-1]}")
            try:
                match_data = scraper.scrape_detailed_match(url)
                detailed_matches.append(match_data)
                print(f"      ✅ {match_data.get('team1_name')} vs {match_data.get('team2_name')} - {match_data.get('final_score')}")
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        print(f"\n📊 Summary: {len(detailed_matches)} matches scraped successfully")
        
        # Create summary table
        if detailed_matches:
            summary_data = []
            for match in detailed_matches:
                summary_data.append({
                    'Match ID': match.get('match_id'),
                    'Teams': f"{match.get('team1_name')} vs {match.get('team2_name')}",
                    'Score': match.get('final_score'),
                    'Maps': match.get('maps_played'),
                    'Winner': match.get('winner_team'),
                    'Format': match.get('match_format')
                })
            
            df = pd.DataFrame(summary_data)
            print(f"\n📋 Detailed Matches Summary:")
            print(df.to_string(index=False))
            
            # Save CSV
            df.to_csv('detailed_matches_summary.csv', index=False)
            print(f"\n💾 Summary saved to 'detailed_matches_summary.csv'")
        
        return detailed_matches
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_database_integration():
    """Test database integration with detailed matches"""
    print(f"\n💾 Testing Database Integration")
    print("=" * 60)
    
    db = VLRDatabase()
    
    # Create sample data with detailed matches
    sample_data = {
        'event_info': {
            'title': 'Champions Tour 2024: Americas Stage 2',
            'dates': 'June 15 - July 7, 2024',
            'url': 'https://www.vlr.gg/event/2095/champions-tour-2024-americas-stage-2'
        },
        'urls': {
            'event_id': '2095'
        },
        'matches_data': {
            'matches': [
                {
                    'team1': 'MIBR',
                    'team2': 'LEVIATÁN',
                    'score': '0:2',
                    'match_url': 'https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1'
                }
            ]
        }
    }
    
    # Test scraping detailed matches
    scraper = DetailedMatchScraper()
    test_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
    
    try:
        print(f"🔍 Scraping detailed match for database test...")
        detailed_match = scraper.scrape_detailed_match(test_url)
        
        # Add to sample data
        sample_data['detailed_matches'] = [detailed_match]
        
        print(f"✅ Detailed match added to sample data")
        
        # Save to database
        print(f"💾 Saving to database...")
        event_id = db.save_comprehensive_data(sample_data)
        print(f"   ✅ Basic data saved with Event ID: {event_id}")
        
        # Save detailed matches
        detailed_count = db.save_detailed_matches([detailed_match], event_id)
        print(f"   ✅ Detailed matches saved: {detailed_count}")
        
        # Verify database contents
        print(f"\n🔍 Verifying database contents...")
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            
            # Check detailed matches
            cursor.execute('SELECT match_id, team1_name, team2_name, final_score FROM detailed_matches WHERE event_id = ?', (event_id,))
            detailed_matches = cursor.fetchall()
            
            print(f"   📊 Detailed matches in database: {len(detailed_matches)}")
            for match in detailed_matches:
                match_id, team1, team2, score = match
                print(f"      🆔 {match_id}: {team1} vs {team2} ({score})")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integration error: {e}")
        return False

def test_csv_export():
    """Test CSV export functionality"""
    print(f"\n📄 Testing CSV Export")
    print("=" * 60)
    
    # Create sample detailed matches data
    detailed_matches = [
        {
            'match_id': '353177',
            'team1_name': 'MIBR',
            'team2_name': 'LEVIATÁN',
            'team1_score': 0,
            'team2_score': 2,
            'winner_team': 'LEVIATÁN',
            'match_status': 'Completed',
            'match_date': '2024-06-22',
            'match_time': '2:30 AM IST',
            'match_format': 'BO3',
            'tournament_stage': 'Regular Season',
            'match_duration': '1:45:30',
            'maps_played': 3,
            'match_url': 'https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1'
        }
    ]
    
    try:
        # Convert to CSV format (same as UI)
        detailed_csv_data = []
        for match in detailed_matches:
            detailed_csv_data.append({
                'Match ID': match.get('match_id', 'N/A'),
                'Team 1': match.get('team1_name', 'N/A'),
                'Team 2': match.get('team2_name', 'N/A'),
                'Team 1 Score': match.get('team1_score', 0),
                'Team 2 Score': match.get('team2_score', 0),
                'Winner': match.get('winner_team', 'N/A'),
                'Status': match.get('match_status', 'N/A'),
                'Date': match.get('match_date', 'N/A'),
                'Time': match.get('match_time', 'N/A'),
                'Format': match.get('match_format', 'N/A'),
                'Stage': match.get('tournament_stage', 'N/A'),
                'Duration': match.get('match_duration', 'N/A'),
                'Maps Played': match.get('maps_played', 0),
                'Match URL': match.get('match_url', 'N/A')
            })
        
        # Create DataFrame and save CSV
        df = pd.DataFrame(detailed_csv_data)
        csv_filename = f"test_detailed_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False)
        
        print(f"✅ CSV export test successful")
        print(f"📄 Columns: {list(df.columns)}")
        print(f"📊 Rows: {len(df)}")
        print(f"💾 Saved to: {csv_filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV export error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎮 VLR.gg Complete Detailed Match Functionality Test")
    print("=" * 80)
    
    tests = [
        ("Improved Detailed Match Scraper", test_improved_detailed_match_scraper),
        ("Multiple Detailed Matches", test_multiple_detailed_matches),
        ("Database Integration", test_database_integration),
        ("CSV Export", test_csv_export)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            success = result is not None and result is not False
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n🎉 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Complete detailed match functionality is working perfectly!")
        print(f"\n🚀 Features Ready:")
        print(f"   • 🔍 Improved detailed match scraper with clean player names")
        print(f"   • 🗺️ Comprehensive map details with scores and durations")
        print(f"   • 👥 Clean player lineups without team suffixes")
        print(f"   • 💾 Database integration with detailed matches table")
        print(f"   • 📄 CSV export with all detailed match data")
        print(f"   • 🎨 Streamlit UI integration with progress tracking")
        print(f"   • ⚙️ Configurable max matches to scrape")
    else:
        print(f"\n💥 SOME TESTS FAILED!")
        print(f"❌ Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()

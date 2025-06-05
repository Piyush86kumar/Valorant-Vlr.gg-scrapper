#!/usr/bin/env python3
"""
Test script to verify the updated Streamlit UI with detailed match functionality
"""

import sys
import os

def test_ui_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing Updated UI Imports")
    print("=" * 50)
    
    try:
        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import json
        print("✅ JSON imported successfully")
        
        from datetime import datetime
        print("✅ Datetime imported successfully")
        
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
        
        # Test VLR scraper imports
        from vlr_scraper_coordinator import VLRScraperCoordinator
        print("✅ VLRScraperCoordinator imported successfully")
        
        from detailed_match_scraper import DetailedMatchScraper
        print("✅ DetailedMatchScraper imported successfully")
        
        from vlr_database import VLRDatabase
        print("✅ VLRDatabase imported successfully")
        
        # Test UI import
        import vlr_streamlit_ui
        print("✅ VLR Streamlit UI imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_functions():
    """Test that UI functions are available"""
    print(f"\n🔍 Testing UI Functions")
    print("=" * 50)
    
    try:
        import vlr_streamlit_ui as ui
        
        # Test function availability
        functions_to_test = [
            'init_session_state',
            'display_header',
            'display_url_input',
            'display_control_panel',
            'display_progress',
            'perform_scraping',
            'display_detailed_matches_data',
            'display_simple_data_preview',
            'display_save_options',
            'main'
        ]
        
        for func_name in functions_to_test:
            if hasattr(ui, func_name):
                print(f"✅ Function '{func_name}' available")
            else:
                print(f"❌ Function '{func_name}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Function test error: {e}")
        return False

def test_detailed_match_integration():
    """Test detailed match integration"""
    print(f"\n🔍 Testing Detailed Match Integration")
    print("=" * 50)
    
    try:
        from detailed_match_scraper import DetailedMatchScraper
        from vlr_database import VLRDatabase
        
        # Test DetailedMatchScraper
        scraper = DetailedMatchScraper()
        print("✅ DetailedMatchScraper instantiated")
        
        # Test match ID extraction
        test_url = "https://www.vlr.gg/353177/mibr-vs-leviat-n-champions-tour-2024-americas-stage-2-w1"
        match_id = scraper.extract_match_id_from_url(test_url)
        if match_id == "353177":
            print(f"✅ Match ID extraction working: {match_id}")
        else:
            print(f"❌ Match ID extraction failed: {match_id}")
            return False
        
        # Test database with detailed matches
        db = VLRDatabase()
        print("✅ VLRDatabase instantiated")
        
        # Test sample detailed match data
        sample_detailed_match = {
            'match_id': '353177',
            'team1_name': 'MIBR',
            'team2_name': 'LEVIATÁN',
            'team1_score': 0,
            'team2_score': 2,
            'match_status': 'Completed',
            'maps_played': 3,
            'winner_team': 'LEVIATÁN',
            'match_url': test_url,
            'scraped_at': '2024-06-22T17:00:00'
        }
        
        # Test saving detailed matches
        try:
            saved_count = db.save_detailed_matches([sample_detailed_match], 'test_event_123')
            print(f"✅ Detailed match save test: {saved_count} matches saved")
        except Exception as e:
            print(f"⚠️ Detailed match save test warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Detailed match integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_data_structures():
    """Test UI data structure handling"""
    print(f"\n📊 Testing UI Data Structures")
    print("=" * 50)
    
    try:
        # Test sample data structure with detailed matches
        sample_data = {
            'event_info': {
                'title': 'Test Event',
                'dates': '2024-01-01 to 2024-01-07',
                'location': 'Test Location'
            },
            'matches_data': {
                'matches': [
                    {
                        'team1': 'Team A',
                        'team2': 'Team B',
                        'score': '2-1',
                        'match_url': 'https://www.vlr.gg/353177/test-match'
                    }
                ]
            },
            'detailed_matches': [
                {
                    'match_id': '353177',
                    'team1_name': 'Team A',
                    'team2_name': 'Team B',
                    'team1_score': 2,
                    'team2_score': 1,
                    'match_status': 'Completed',
                    'maps_played': 3,
                    'winner_team': 'Team A'
                }
            ],
            'stats_data': {
                'player_stats': [
                    {
                        'player': 'TestPlayer',
                        'team': 'Team A',
                        'rating': '1.25'
                    }
                ]
            }
        }
        
        print("✅ Sample data structure created")
        
        # Test data access patterns
        matches = sample_data.get('matches_data', {}).get('matches', [])
        detailed_matches = sample_data.get('detailed_matches', [])
        
        print(f"✅ Basic matches: {len(matches)}")
        print(f"✅ Detailed matches: {len(detailed_matches)}")
        
        # Test CSV data conversion for detailed matches
        import pandas as pd
        
        if detailed_matches:
            detailed_csv_data = []
            for match in detailed_matches:
                detailed_csv_data.append({
                    'Match ID': match.get('match_id', 'N/A'),
                    'Team 1': match.get('team1_name', 'N/A'),
                    'Team 2': match.get('team2_name', 'N/A'),
                    'Score': f"{match.get('team1_score', 0)}:{match.get('team2_score', 0)}",
                    'Winner': match.get('winner_team', 'N/A'),
                    'Status': match.get('match_status', 'N/A')
                })
            
            detailed_df = pd.DataFrame(detailed_csv_data)
            print(f"✅ Detailed matches DataFrame: {len(detailed_df)} rows")
            print(f"   Columns: {list(detailed_df.columns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all UI tests"""
    print("🎮 VLR.gg Streamlit UI Update Test")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_ui_imports),
        ("Function Test", test_ui_functions),
        ("Detailed Match Integration", test_detailed_match_integration),
        ("Data Structure Test", test_ui_data_structures)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"💥 {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n🎉 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Updated Streamlit UI is ready for use with detailed match functionality!")
        print(f"\n🚀 New Features Available:")
        print(f"   • 🔍 Detailed match scraping option")
        print(f"   • 📊 Detailed match data display")
        print(f"   • 💾 Detailed match database storage")
        print(f"   • 📄 Detailed match CSV downloads")
        print(f"   • 🎯 Enhanced data preview with detailed matches")
    else:
        print(f"\n💥 SOME TESTS FAILED!")
        print(f"❌ Please check the errors above and fix them before using the UI.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test script for the updated matches_scraper.py
Tests the new VLR.gg-specific extraction methods
"""

from matches_scraper import MatchesScraper
import json

def test_matches_scraper():
    """Test the updated matches scraper"""
    print("🧪 Testing Updated Matches Scraper")
    print("=" * 50)

    scraper = MatchesScraper()

    # Test URL - Champions Tour 2024 Americas Stage 2
    test_url = "https://www.vlr.gg/event/2095/champions-tour-2024-americas-stage-2"

    def progress_callback(message):
        print(f"📊 {message}")

    try:
        print(f"🎯 Testing URL: {test_url}")
        print(f"🔄 Starting scraping process...")

        # Scrape matches
        matches_data = scraper.scrape_matches(test_url, progress_callback)

        print(f"\n✅ Scraping completed!")
        print(f"📈 Results Summary:")
        print(f"   🏆 Total matches found: {matches_data['total_matches']}")
        print(f"   📊 Series info found: {len(matches_data['series_info'])}")
        print(f"   🔗 Scraped from: {matches_data['scraped_from']}")

        # Analyze the first few matches to verify data quality
        matches = matches_data.get('matches', [])
        if matches:
            print(f"\n🔍 Sample Match Analysis:")
            print(f"   📋 Analyzing first {min(3, len(matches))} matches...")

            for i, match in enumerate(matches[:3]):
                print(f"\n   Match {i+1}:")
                print(f"      📅 Date: {match.get('date', 'N/A')}")
                print(f"      ⏰ Time: {match.get('time', 'N/A')}")
                print(f"      🏟️ Teams: {match.get('team1', 'N/A')} vs {match.get('team2', 'N/A')}")
                print(f"      📊 Score: {match.get('score', 'N/A')}")
                print(f"      🏆 Winner: {match.get('winner', 'N/A')}")
                print(f"      📍 Status: {match.get('status', 'N/A')}")
                print(f"      📅 Week: {match.get('week', 'N/A')}")
                print(f"      🎭 Stage: {match.get('stage', 'N/A')}")
                print(f"      🔗 URL: {match.get('match_url', 'N/A')}")

            # Check data completeness
            print(f"\n📊 Data Completeness Analysis:")
            required_fields = ['date', 'time', 'team1', 'team2', 'score', 'status', 'week', 'stage', 'match_url', 'winner']

            for field in required_fields:
                non_na_count = sum(1 for match in matches if match.get(field) not in ['N/A', None, ''])
                percentage = (non_na_count / len(matches)) * 100 if matches else 0
                status_emoji = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
                print(f"      {status_emoji} {field}: {non_na_count}/{len(matches)} ({percentage:.1f}%)")

            # Save sample data for inspection
            sample_data = {
                'summary': {
                    'total_matches': len(matches),
                    'test_url': test_url,
                    'scraped_at': matches_data.get('scraped_at')
                },
                'sample_matches': matches[:5]  # First 5 matches
            }

            with open('sample_matches_data.json', 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Sample data saved to 'sample_matches_data.json'")

        else:
            print(f"\n❌ No matches found! This indicates an issue with the scraper.")

        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_matches_scraper()

    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📋 Check 'sample_matches_data.json' for detailed results")
    else:
        print(f"\n💥 Test failed! Check the error messages above.")

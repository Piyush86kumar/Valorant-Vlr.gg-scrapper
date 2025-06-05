#!/usr/bin/env python3
"""
Test script for the updated player_stats_scraper.py
Tests the new VLR.gg-specific extraction methods
"""

from player_stats_scraper import PlayerStatsScraper
import json

def test_player_stats_scraper():
    """Test the updated player stats scraper"""
    print("🧪 Testing Updated Player Stats Scraper")
    print("=" * 50)

    scraper = PlayerStatsScraper()

    # Test URL - Champions Tour 2024 Americas Stage 2 stats
    test_url = "https://www.vlr.gg/event/stats/2095/champions-tour-2024-americas-stage-2"

    def progress_callback(message):
        print(f"📊 {message}")

    try:
        print(f"🎯 Testing URL: {test_url}")
        print(f"🔄 Starting scraping process...")

        # Scrape player stats
        stats_data = scraper.scrape_player_stats(test_url, progress_callback)

        print(f"\n✅ Scraping completed!")
        print(f"📈 Results Summary:")
        print(f"   👥 Total players found: {stats_data['total_players']}")
        print(f"   🔗 Scraped from: {stats_data['scraped_from']}")

        # Analyze the first few players to verify data quality
        players = stats_data.get('players', [])
        if players:
            print(f"\n🔍 Sample Player Analysis:")
            print(f"   📋 Analyzing first {min(5, len(players))} players...")

            for i, player in enumerate(players[:5]):
                print(f"\n   Player {i+1}:")
                print(f"      🆔 ID: {player.get('player_id', 'N/A')}")
                print(f"      👤 Name: {player.get('player', 'N/A')} ({player.get('player_name', 'N/A')})")
                print(f"      🏟️ Team: {player.get('team', 'N/A')}")
                print(f"      🎭 Agents: {player.get('agents_display', 'N/A')} ({player.get('agents_count', 0)} total)")
                print(f"      🎯 Rating: {player.get('rating', 'N/A')}")
                print(f"      📊 ACS: {player.get('acs', 'N/A')}")
                print(f"      ⚔️ K:D: {player.get('kd_ratio', 'N/A')}")
                print(f"      🎯 KAST: {player.get('kast', 'N/A')}")
                print(f"      💥 ADR: {player.get('adr', 'N/A')}")
                print(f"      🔫 Kills: {player.get('kills', 'N/A')}")
                print(f"      💀 Deaths: {player.get('deaths', 'N/A')}")
                print(f"      🤝 Assists: {player.get('assists', 'N/A')}")
                print(f"      🔗 URL: {player.get('player_url', 'N/A')}")

            # Check data completeness
            print(f"\n📊 Data Completeness Analysis:")
            required_fields = [
                'player_id', 'player', 'player_name', 'team', 'agents_display', 'agents_count',
                'rating', 'acs', 'kd_ratio', 'kast', 'adr', 'kills', 'deaths', 'assists',
                'rounds', 'kpr', 'apr', 'fkpr', 'fdpr', 'hs_percent', 'cl_percent',
                'clutches', 'k_max', 'first_kills', 'first_deaths'
            ]

            for field in required_fields:
                non_na_count = sum(1 for player in players if player.get(field) not in ['N/A', None, ''])
                percentage = (non_na_count / len(players)) * 100 if players else 0
                status_emoji = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
                print(f"      {status_emoji} {field}: {non_na_count}/{len(players)} ({percentage:.1f}%)")

            # Save sample data for inspection
            sample_data = {
                'summary': {
                    'total_players': len(players),
                    'test_url': test_url,
                    'scraped_at': stats_data.get('scraped_at')
                },
                'sample_players': players[:10]  # First 10 players
            }

            with open('sample_player_stats_data.json', 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Sample data saved to 'sample_player_stats_data.json'")

            # Show top performers
            print(f"\n🏆 Top Performers:")

            # Sort by ACS (Average Combat Score)
            try:
                acs_sorted = sorted(
                    [p for p in players if p.get('acs', 'N/A') != 'N/A'],
                    key=lambda x: float(x['acs']),
                    reverse=True
                )
                print(f"   📊 Top 3 by ACS:")
                for i, player in enumerate(acs_sorted[:3]):
                    print(f"      {i+1}. {player.get('player_name', 'N/A')} ({player.get('team', 'N/A')}): {player.get('acs', 'N/A')}")
            except (ValueError, TypeError):
                print(f"   📊 Could not sort by ACS (data format issue)")

            # Sort by Rating
            try:
                rating_sorted = sorted(
                    [p for p in players if p.get('rating', 'N/A') != 'N/A'],
                    key=lambda x: float(x['rating']),
                    reverse=True
                )
                print(f"   🎯 Top 3 by Rating:")
                for i, player in enumerate(rating_sorted[:3]):
                    print(f"      {i+1}. {player.get('player_name', 'N/A')} ({player.get('team', 'N/A')}): {player.get('rating', 'N/A')}")
            except (ValueError, TypeError):
                print(f"   🎯 Could not sort by Rating (data format issue)")

        else:
            print(f"\n❌ No players found! This indicates an issue with the scraper.")

        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_player_stats_scraper()

    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📋 Check 'sample_player_stats_data.json' for detailed results")
    else:
        print(f"\n💥 Test failed! Check the error messages above.")

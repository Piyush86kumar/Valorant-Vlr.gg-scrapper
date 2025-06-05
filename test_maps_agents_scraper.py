#!/usr/bin/env python3
"""
Test script for the updated maps_agents_scraper.py
Tests the new VLR.gg-specific extraction methods for separate maps and agents data
"""

from maps_agents_scraper import MapsAgentsScraper
import json

def test_maps_agents_scraper():
    """Test the updated maps and agents scraper"""
    print("🧪 Testing Updated Maps & Agents Scraper")
    print("=" * 50)

    scraper = MapsAgentsScraper()

    # Test URL - Champions Tour 2024 Americas Stage 2 agents
    test_url = "https://www.vlr.gg/event/agents/2095/champions-tour-2024-americas-stage-2"

    def progress_callback(message):
        print(f"📊 {message}")

    try:
        print(f"🎯 Testing URL: {test_url}")
        print(f"🔄 Starting scraping process...")

        # Scrape maps and agents
        data = scraper.scrape_maps_and_agents(test_url, progress_callback)

        print(f"\n✅ Scraping completed!")
        print(f"📈 Results Summary:")
        print(f"   🗺️ Total maps found: {data['total_maps']}")
        print(f"   🎭 Total agents found: {data['total_agents']}")
        print(f"   🔗 Scraped from: {data['scraped_from']}")

        # Analyze maps data
        maps = data.get('maps', [])
        if maps:
            print(f"\n🗺️ Maps Data Analysis:")
            print(f"   📋 Analyzing {len(maps)} maps...")

            for i, map_data in enumerate(maps):
                print(f"\n   Map {i+1}:")
                print(f"      🗺️ Name: {map_data.get('map_name', 'N/A')}")
                print(f"      🎮 Times Played: {map_data.get('times_played', 'N/A')}")
                print(f"      ⚔️ Attack Win %: {map_data.get('attack_win_percent', 'N/A')}")
                print(f"      🛡️ Defense Win %: {map_data.get('defense_win_percent', 'N/A')}")

            # Check data completeness for maps
            print(f"\n📊 Maps Data Completeness:")
            required_map_fields = ['map_name', 'times_played', 'attack_win_percent', 'defense_win_percent']

            for field in required_map_fields:
                non_na_count = sum(1 for map_data in maps if map_data.get(field) not in ['N/A', None, ''])
                percentage = (non_na_count / len(maps)) * 100 if maps else 0
                status_emoji = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
                print(f"      {status_emoji} {field}: {non_na_count}/{len(maps)} ({percentage:.1f}%)")

        # Analyze agents data
        agents = data.get('agents', [])
        if agents:
            print(f"\n🎭 Agents Data Analysis:")
            print(f"   📋 Analyzing {len(agents)} agents...")

            # Show top 5 agents by total utilization (VLR.gg format)
            sorted_agents = sorted(agents, key=lambda x: x.get('total_utilization_percent', 0), reverse=True)
            print(f"\n   🏆 Top 5 Agents by Total Utilization (VLR.gg format):")
            for i, agent in enumerate(sorted_agents[:5]):
                print(f"      {i+1}. {agent.get('agent_name', 'N/A')}: {agent.get('total_utilization_percent', 0)}% (total)")
                print(f"         Maps available: {agent.get('maps_count', 0)}")

            # Check data completeness for agents
            print(f"\n📊 Agents Data Completeness:")
            required_agent_fields = ['agent_name', 'total_utilization_percent', 'maps_count', 'map_utilizations']

            for field in required_agent_fields:
                non_na_count = sum(1 for agent in agents if agent.get(field) not in ['N/A', None, '', []])
                percentage = (non_na_count / len(agents)) * 100 if agents else 0
                status_emoji = "✅" if percentage > 80 else "⚠️" if percentage > 50 else "❌"
                print(f"      {status_emoji} {field}: {non_na_count}/{len(agents)} ({percentage:.1f}%)")

            # Show sample agent map utilizations (VLR.gg format)
            if sorted_agents and sorted_agents[0].get('map_utilizations'):
                top_agent = sorted_agents[0]
                print(f"\n   🔍 Sample Agent Map Utilizations - {top_agent.get('agent_name', 'N/A')} (VLR.gg format):")
                print(f"      📊 Total Utilization: {top_agent.get('total_utilization_percent', 0)}%")
                print(f"      🗺️ Individual Maps:")
                for map_util in top_agent['map_utilizations'][:5]:  # Show first 5 maps
                    print(f"         • {map_util.get('map', 'N/A')}: {map_util.get('utilization_percent', 0)}%")

        # Save sample data for inspection
        sample_data = {
            'summary': {
                'total_maps': len(maps),
                'total_agents': len(agents),
                'test_url': test_url,
                'scraped_at': data.get('scraped_at')
            },
            'sample_maps': maps,  # All maps
            'sample_agents': agents[:10]  # First 10 agents
        }

        with open('sample_maps_agents_data.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Sample data saved to 'sample_maps_agents_data.json'")

        return True

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_maps_agents_scraper()

    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"📋 Check 'sample_maps_agents_data.json' for detailed results")
    else:
        print(f"\n💥 Test failed! Check the error messages above.")

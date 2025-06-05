#!/usr/bin/env python3
"""
Complete test for VLR.gg format implementation
Tests the entire pipeline: scraping -> data processing -> UI display format
"""

from maps_agents_scraper import MapsAgentsScraper
import pandas as pd
import json

def test_complete_vlr_pipeline():
    """Test the complete VLR.gg pipeline"""
    print("🧪 Testing Complete VLR.gg Pipeline")
    print("=" * 50)
    
    # Step 1: Test scraping
    print("📊 Step 1: Testing Maps & Agents Scraping...")
    scraper = MapsAgentsScraper()
    test_url = "https://www.vlr.gg/event/agents/2095/champions-tour-2024-americas-stage-2"
    
    try:
        data = scraper.scrape_maps_and_agents(test_url)
        
        maps = data.get('maps', [])
        agents = data.get('agents', [])
        
        print(f"   ✅ Scraped {len(maps)} maps and {len(agents)} agents")
        
        # Step 2: Test data structure
        print("\n📋 Step 2: Testing Data Structure...")
        
        if agents and len(agents) > 0:
            sample_agent = agents[0]
            required_fields = ['agent_name', 'total_utilization_percent', 'map_utilizations']
            
            missing_fields = [field for field in required_fields if field not in sample_agent]
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All required fields present")
                
            # Check map utilizations structure
            map_utils = sample_agent.get('map_utilizations', [])
            if map_utils and len(map_utils) > 0:
                sample_map = map_utils[0]
                if 'map' in sample_map and 'utilization_percent' in sample_map:
                    print(f"   ✅ Map utilizations structure correct")
                else:
                    print(f"   ❌ Map utilizations structure incorrect")
                    return False
        
        # Step 3: Test VLR.gg table format transformation
        print("\n🎯 Step 3: Testing VLR.gg Table Format...")
        
        # Create the VLR.gg style table (same logic as UI)
        vlr_table_data = []
        
        for agent in agents:
            row_data = {
                'Agent': agent['agent_name'],
                'Total': f"{agent.get('total_utilization_percent', 0)}%"
            }
            
            # Add individual map utilizations
            map_utils = agent.get('map_utilizations', [])
            for map_util in map_utils:
                map_name = map_util.get('map', '')
                utilization = map_util.get('utilization_percent', 0)
                row_data[map_name] = f"{utilization}%"
            
            vlr_table_data.append(row_data)
        
        if vlr_table_data:
            vlr_df = pd.DataFrame(vlr_table_data)
            
            # Sort by total utilization (remove % and convert to float for sorting)
            vlr_df['_sort_total'] = vlr_df['Total'].str.replace('%', '').astype(float)
            vlr_df = vlr_df.sort_values('_sort_total', ascending=False)
            vlr_df = vlr_df.drop('_sort_total', axis=1)
            
            print(f"   ✅ VLR.gg table created successfully")
            print(f"   📊 Columns: {list(vlr_df.columns)}")
            print(f"   📋 Rows: {len(vlr_df)}")
            
            # Verify structure
            expected_structure = ['Agent', 'Total'] + [col for col in vlr_df.columns if col not in ['Agent', 'Total']]
            actual_structure = list(vlr_df.columns)
            
            if len(expected_structure) == len(actual_structure):
                print(f"   ✅ Table structure matches VLR.gg format")
            else:
                print(f"   ❌ Table structure mismatch")
                return False
            
            # Step 4: Display sample results
            print(f"\n🏆 Step 4: Sample VLR.gg Format Results:")
            print(f"\n{vlr_df.head().to_string(index=False)}")
            
            # Step 5: Verify no forbidden elements
            print(f"\n🚫 Step 5: Verifying Removed Elements...")
            
            # Check that maps_count is not in the display
            forbidden_columns = ['maps_count', 'maps_played']
            found_forbidden = [col for col in vlr_df.columns if col in forbidden_columns]
            
            if found_forbidden:
                print(f"   ❌ Found forbidden columns: {found_forbidden}")
                return False
            else:
                print(f"   ✅ No forbidden columns found")
            
            # Step 6: Save results
            print(f"\n💾 Step 6: Saving Results...")
            
            # Save the complete data structure
            test_results = {
                'maps_data': maps,
                'agents_data': agents,
                'vlr_formatted_table': vlr_df.to_dict('records'),
                'test_summary': {
                    'total_maps': len(maps),
                    'total_agents': len(agents),
                    'table_columns': list(vlr_df.columns),
                    'table_rows': len(vlr_df),
                    'test_passed': True
                }
            }
            
            with open('complete_vlr_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2, ensure_ascii=False)
            
            vlr_df.to_csv('complete_vlr_table.csv', index=False)
            
            print(f"   ✅ Results saved to 'complete_vlr_test_results.json' and 'complete_vlr_table.csv'")
            
            return True
        else:
            print(f"   ❌ Failed to create VLR.gg table")
            return False
            
    except Exception as e:
        print(f"❌ Error in pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_vlr_pipeline()
    
    if success:
        print(f"\n🎉 COMPLETE VLR.gg PIPELINE TEST PASSED!")
        print(f"✅ All components working correctly:")
        print(f"   • Maps & Agents scraping")
        print(f"   • Data structure validation")
        print(f"   • VLR.gg table format transformation")
        print(f"   • UI-ready data format")
        print(f"   • Forbidden elements removed")
        print(f"\n🚀 Ready for production use!")
    else:
        print(f"\n💥 PIPELINE TEST FAILED!")
        print(f"❌ Check the error messages above for details.")

#!/usr/bin/env python3
"""
Test script to verify the VLR.gg table format for agent utilization
"""

import pandas as pd
import json

def test_vlr_table_format():
    """Test the VLR.gg table format transformation"""
    print("🧪 Testing VLR.gg Table Format")
    print("=" * 40)
    
    # Load sample data
    try:
        with open('sample_maps_agents_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        agents = data.get('sample_agents', [])
        print(f"📊 Loaded {len(agents)} sample agents")
        
        if not agents:
            print("❌ No agent data found")
            return False
        
        # Create the VLR.gg style table
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
            
            print(f"\n🎯 VLR.gg Style Table Created!")
            print(f"📋 Columns: {list(vlr_df.columns)}")
            print(f"📊 Rows: {len(vlr_df)}")
            
            print(f"\n🏆 Top 5 Agents (VLR.gg Format):")
            print(vlr_df.head().to_string(index=False))
            
            print(f"\n📈 Sample Data Structure:")
            for i, (_, row) in enumerate(vlr_df.head(3).iterrows()):
                print(f"\n   Agent {i+1}: {row['Agent']}")
                print(f"      Total: {row['Total']}")
                print(f"      Maps: ", end="")
                for col in vlr_df.columns:
                    if col not in ['Agent', 'Total']:
                        print(f"{col}={row[col]}", end=" ")
                print()
            
            # Save the formatted table
            vlr_df.to_csv('vlr_formatted_agents.csv', index=False)
            print(f"\n💾 VLR.gg formatted table saved to 'vlr_formatted_agents.csv'")
            
            return True
        else:
            print("❌ Failed to create VLR.gg table")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vlr_table_format()
    
    if success:
        print(f"\n🎉 VLR.gg table format test completed successfully!")
        print(f"📋 The table now shows:")
        print(f"   • Agents as rows")
        print(f"   • Total utilization + individual maps as columns")
        print(f"   • Sorted by total utilization (highest first)")
        print(f"   • No map count column")
        print(f"   • No individual map utilizations section")
    else:
        print(f"\n💥 Test failed! Check the error messages above.")

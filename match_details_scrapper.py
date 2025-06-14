import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, List, Any, Optional
import time
import re
import json
from datetime import datetime
import traceback

class MatchDetailsScraper:
    def __init__(self):
        self.base_url = "https://www.vlr.gg"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _safe_get_text(self, element: Optional[BeautifulSoup], default: str = 'N/A') -> str:
        """Safely get text from a BeautifulSoup element."""
        return element.get_text(strip=True) if element else default

    def _extract_match_id(self, url: str) -> Optional[str]:
        """Extract the numeric match ID from a VLR.gg match URL."""
        match = re.search(r'/(\d+)/', url)
        return match.group(1) if match else None

    def _parse_player_row_stats(self, row_soup: BeautifulSoup, is_overview_style: bool, team_name: str) -> Dict[str, Any]:
        """Parses a single player's stats from a table row."""
        player_data = {}
        player_data['team_name'] = team_name
        cells = row_soup.find_all('td')

        # Player Name and ID from the first cell
        player_cell = cells[0]
        player_name_tag = player_cell.find('a') # This is the anchor tag for the player

        player_data['player_id'] = None
        if player_name_tag and player_name_tag.has_attr('href'):
            player_url = player_name_tag['href']
            id_match = re.search(r'/player/(\d+)/', player_url)
            if id_match:
                player_data['player_id'] = id_match.group(1)

        player_div_text_of = player_name_tag.find('div', class_='text-of') if player_name_tag else None
        player_data['player_name'] = self._safe_get_text(player_div_text_of, player_cell.get_text(strip=True))

        if is_overview_style: # Agent in a separate column for "All Maps"
            agent_cell = cells[1]
            agent_spans = agent_cell.find_all('span', class_='mod-agent')
            agent_imgs = []
            for span_tag in agent_spans:
                img = span_tag.find('img')
                if img:
                    agent_imgs.append(img)
            player_data['agents'] = [img['alt'] for img in agent_imgs if img and img.has_attr('alt')]
            if not player_data['agents']: # Fallback to title if alt is missing
                 player_data['agents'] = [img['title'] for img in agent_imgs if img and img.has_attr('title')]
            player_data['agent'] = player_data['agents'][0] if player_data['agents'] else 'N/A' # Keep primary agent for compatibility
        else: # Agent in the first column with player name for per-map stats
            # When is_overview_style is False, agent is in the first cell (player_cell)
            player_data['agent'] = 'N/A'
            agent_img_tag = None
            
            # Priority 1: Look for <img> inside <span class="mod-agent">
            # Example: <span class="stats-sq mod-agent small"><img src="...kayo.png" alt="kayo"></span>
            agent_span_mod_agent = player_cell.find('span', class_='mod-agent')
            if agent_span_mod_agent:
                agent_img_tag = agent_span_mod_agent.find('img')
            
            # Priority 2: Look for <img class="mod-agent">
            if not agent_img_tag:
                agent_img_tag = player_cell.find('img', class_='mod-agent')
            
            # Priority 3: Fallback to any <img> if its src looks like an agent image
            if not agent_img_tag:
                all_imgs_in_cell = player_cell.find_all('img')
                for img_candidate in all_imgs_in_cell:
                    img_src = img_candidate.get('src', '')
                    if '/img/vlr/game/agents/' in img_src: # VLR agent images path
                        agent_img_tag = img_candidate
                        break
            
            if agent_img_tag:
                agent_name_candidate = agent_img_tag.get('alt', '')
                if not agent_name_candidate: # Fallback to title
                    agent_name_candidate = agent_img_tag.get('title', '')
                
                agent_name_candidate = agent_name_candidate.strip()
                # Basic validation for agent name
                if agent_name_candidate and len(agent_name_candidate) < 20 and '/' not in agent_name_candidate:
                    player_data['agent'] = agent_name_candidate
                else: # If suspicious, empty, or contains path characters, try to derive from src
                    img_src = agent_img_tag.get('src', '')
                    if '/img/vlr/game/agents/' in img_src:
                        extracted_from_src = img_src.split('/agents/')[-1].split('.')[0].replace('-', ' ')
                        if extracted_from_src and len(extracted_from_src) < 20:
                            player_data['agent'] = extracted_from_src.title() # Use .title() for "Kill Joy" like names
            player_data['agents'] = [player_data['agent']] if player_data['agent'] != 'N/A' else []


        stat_keys = ['rating', 'acs', 'k', 'd', 'a', 'kd_diff', 'kast', 'adr', 'hs_percent', 'fk', 'fd', 'fk_fd_diff']
        stat_start_index = 2 if is_overview_style else 1

        player_data['stats_all_sides'] = {}
        player_data['stats_attack'] = {}
        player_data['stats_defense'] = {}

        for i, key_name in enumerate(stat_keys):
            cell_index = stat_start_index + i
            if cell_index < len(cells):
                stat_cell = cells[cell_index]
                
                # --- Extracting 'stats_all_sides' ---
                stat_value_all_sides = "N/A"
                # Try most specific first: <span class="side mod-side mod-both">VALUE</span>
                target_span = stat_cell.find('span', class_='side mod-side mod-both')
                if target_span:
                    stat_value_all_sides = self._safe_get_text(target_span)
                
                # Fallback 1: <span class="mod-both">VALUE</span>
                if stat_value_all_sides == "N/A" or stat_value_all_sides == "":
                    target_span = stat_cell.find('span', class_='mod-both')
                    if target_span:
                        stat_value_all_sides = self._safe_get_text(target_span)
                
                # Fallback 2: <span class="stats-sq">VALUE</span> (if it doesn't contain separate T/CT sides)
                if stat_value_all_sides == "N/A" or stat_value_all_sides == "":
                    stats_sq_span = stat_cell.find('span', class_='stats-sq')
                    if stats_sq_span:
                        if not (stats_sq_span.find('span', class_='mod-t') or stats_sq_span.find('span', class_='mod-ct')):
                            stat_value_all_sides = self._safe_get_text(stats_sq_span)
                
                # Fallback 3: Direct text of the cell if no T/CT breakdown
                if stat_value_all_sides == "N/A" or stat_value_all_sides == "":
                    if not (stat_cell.find('span', class_='mod-t') or stat_cell.find('span', class_='mod-ct')):
                        stat_value_all_sides = self._safe_get_text(stat_cell)
                
                player_data['stats_all_sides'][key_name] = "N/A" if stat_value_all_sides == "" else stat_value_all_sides

                # --- Extracting 'stats_attack' ---
                stat_value_attack = "N/A"
                target_span_t = stat_cell.find('span', class_='side mod-side mod-t')
                if not target_span_t: target_span_t = stat_cell.find('span', class_='mod-t')
                if target_span_t: stat_value_attack = self._safe_get_text(target_span_t)
                player_data['stats_attack'][key_name] = "N/A" if stat_value_attack == "" else stat_value_attack

                # --- Extracting 'stats_defense' ---
                stat_value_defense = "N/A"
                target_span_ct = stat_cell.find('span', class_='side mod-side mod-ct')
                if not target_span_ct: target_span_ct = stat_cell.find('span', class_='mod-ct')
                if target_span_ct: stat_value_defense = self._safe_get_text(target_span_ct)
                player_data['stats_defense'][key_name] = "N/A" if stat_value_defense == "" else stat_value_defense
            else:
                player_data['stats_all_sides'][key_name] = 'N/A'
                player_data['stats_attack'][key_name] = 'N/A'
                player_data['stats_defense'][key_name] = 'N/A'
        return player_data

    def _parse_player_stats_table(self, table_soup: BeautifulSoup, is_overview_style: bool, team_name: str) -> List[Dict[str, Any]]:
        """Parses a full player stats table (e.g., for one team on one map)."""
        player_stats_list = []
        stat_rows = table_soup.find('tbody').find_all('tr') if table_soup.find('tbody') else []
        for row_soup in stat_rows:
            player_stats_list.append(self._parse_player_row_stats(row_soup, is_overview_style, team_name))
        return player_stats_list

    def _extract_match_header_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extracts information from the main match header.
        """
        header_info = {
            'event_name': 'N/A', 'event_stage': 'N/A', 'match_date_utc': 'N/A',
            'patch': 'N/A', 'team1_name': 'N/A', 'team2_name': 'N/A',
            'team1_score_overall': 0, 'team2_score_overall': 0,
            'match_format': 'N/A', 'map_picks_bans_note': 'N/A'
        }
        match_header_super = soup.find('div', class_='match-header-super')
        if match_header_super:
            event_link_tag = match_header_super.find('a', class_='match-header-event')
            if event_link_tag:
                event_divs = event_link_tag.find_all('div', recursive=False)
                if len(event_divs) > 0 and event_divs[0].find('div'): # Check for nested div for event name
                     header_info['event_name'] = self._safe_get_text(event_divs[0].find_all('div')[0])
                     if len(event_divs[0].find_all('div')) > 1:
                        header_info['event_stage'] = self._safe_get_text(event_divs[0].find_all('div')[1]) # Second div for stage

            date_container = match_header_super.find('div', class_='match-header-date')
            if date_container:
                moment_tag = date_container.find('div', class_='moment-tz-convert')
                if moment_tag and moment_tag.has_attr('data-utc-ts'):
                    header_info['match_date_utc'] = moment_tag['data-utc-ts']
                patch_tag = date_container.find('div', style=lambda x: x and 'italic' in x)
                header_info['patch'] = self._safe_get_text(patch_tag)

        match_header_vs = soup.find('div', class_='match-header-vs')
        if match_header_vs:
            team1_tag = match_header_vs.find('a', class_='match-header-link mod-1')
            if team1_tag:
                 header_info['team1_name'] = self._safe_get_text(team1_tag.find('div', class_='wf-title-med'))

            team2_tag = match_header_vs.find('a', class_='match-header-link mod-2')
            if team2_tag:
                header_info['team2_name'] = self._safe_get_text(team2_tag.find('div', class_='wf-title-med'))

            score_container = match_header_vs.find('div', class_='match-header-vs-score')
            if score_container:
                score_spoiler = score_container.find('div', class_='js-spoiler')
                if score_spoiler:
                    scores = score_spoiler.find_all('span')
                    if len(scores) == 3: # Winner : Loser
                        try:
                            s1 = int(self._safe_get_text(scores[0], '0'))
                            s2 = int(self._safe_get_text(scores[2], '0'))
                            # Determine which score belongs to team1 based on winner/loser class
                            if 'match-header-vs-score-winner' in scores[0].get('class', []):
                                header_info['team1_score_overall'] = s1
                                header_info['team2_score_overall'] = s2
                            elif 'match-header-vs-score-winner' in scores[2].get('class', []):
                                header_info['team1_score_overall'] = s2
                                header_info['team2_score_overall'] = s1
                            else: # Fallback if winner class is not present on score spans, assume order
                                header_info['team1_score_overall'] = s1
                                header_info['team2_score_overall'] = s2
                        except ValueError:
                            pass # Scores remain 0
                
                format_tag_elements = score_container.find_all('div', class_='match-header-vs-note')
                if len(format_tag_elements) > 1 : # Second one is usually format
                    header_info['match_format'] = self._safe_get_text(format_tag_elements[1])
                elif len(format_tag_elements) == 1 and "final" not in format_tag_elements[0].get_text(strip=True).lower(): # If only one and not "final"
                    header_info['match_format'] = self._safe_get_text(format_tag_elements[0])


        map_note_tag = soup.find('div', class_='match-header-note') # This is usually for picks/bans
        header_info['map_picks_bans_note'] = self._safe_get_text(map_note_tag)
        return header_info

    def _extract_maps_data(self, soup: BeautifulSoup, team1_name_overall: str, team2_name_overall: str) -> List[Dict[str, Any]]:
        """Extracts data for each map played."""
        maps_data_list = []
        map_sections = soup.select('div.vm-stats-container > div.vm-stats-game[data-game-id]:not([data-game-id="all"])')

        for i, map_section_soup in enumerate(map_sections):
            map_data = {'map_order': i + 1, 'player_stats': {team1_name_overall: [], team2_name_overall: []}}
            
            header = map_section_soup.find('div', class_='vm-stats-game-header')
            if not header: continue # Skip if no header

            map_info_div = header.find('div', class_='map')
            if not map_info_div: continue # Skip if no map info

            map_name_container = map_info_div.find('div', style=lambda x: x and 'font-weight: 700' in x)
            map_name_span = map_name_container.find('span') if map_name_container else None
            map_data['map_name'] = self._safe_get_text(map_name_span).replace('PICK', '').strip()
            map_data['map_duration'] = self._safe_get_text(map_info_div.find('div', class_='map-duration'))
            
            if map_name_span:
                picked_by_span = map_name_span.find('span', class_=lambda x: x and 'picked' in x)
                if picked_by_span:
                    if 'mod-1' in picked_by_span.get('class', []): # Team 1 picked
                        map_data['picked_by'] = team1_name_overall
                    elif 'mod-2' in picked_by_span.get('class', []): # Team 2 picked
                        map_data['picked_by'] = team2_name_overall
                    else:
                        map_data['picked_by'] = "Decider" 
                else:
                     map_data['picked_by'] = "Decider"
            else:
                map_data['picked_by'] = "N/A"


            scores = header.find_all('div', class_='score')
            if len(scores) >= 2:
                map_data['team1_score_map'] = int(self._safe_get_text(scores[0], '0'))
                map_data['team2_score_map'] = int(self._safe_get_text(scores[1], '0'))

                if map_data['team1_score_map'] > map_data['team2_score_map']:
                    map_data['winner_team_name'] = team1_name_overall
                elif map_data['team2_score_map'] > map_data['team1_score_map']:
                    map_data['winner_team_name'] = team2_name_overall
                else:
                    map_data['winner_team_name'] = "Draw"
            else:
                map_data['team1_score_map'] = 0
                map_data['team2_score_map'] = 0
                map_data['winner_team_name'] = "N/A"


            player_stat_tables = map_section_soup.select('div > table.wf-table-inset.mod-overview') 
            if len(player_stat_tables) >= 1:
                 map_data['player_stats'][team1_name_overall] = self._parse_player_stats_table(player_stat_tables[0], is_overview_style=False, team_name=team1_name_overall)
            if len(player_stat_tables) >= 2:
                 map_data['player_stats'][team2_name_overall] = self._parse_player_stats_table(player_stat_tables[1], is_overview_style=False, team_name=team2_name_overall)

            maps_data_list.append(map_data)
        return maps_data_list

    def _extract_overall_player_stats(self, soup: BeautifulSoup, team1_name_overall: str, team2_name_overall: str) -> Dict[str, List[Dict[str, Any]]]:
        """Extracts player stats from the 'All Maps' overview section."""
        overall_stats = {team1_name_overall: [], team2_name_overall: []}
        all_maps_section = soup.find('div', class_='vm-stats-game', attrs={'data-game-id': 'all'})
        if all_maps_section:
            player_stat_tables = all_maps_section.select('div > table.wf-table-inset.mod-overview')
            if len(player_stat_tables) >= 1:
                overall_stats[team1_name_overall] = self._parse_player_stats_table(player_stat_tables[0], is_overview_style=True, team_name=team1_name_overall)
            if len(player_stat_tables) >= 2:
                overall_stats[team2_name_overall] = self._parse_player_stats_table(player_stat_tables[1], is_overview_style=True, team_name=team2_name_overall)
        return overall_stats

    def get_match_details(self, match_url: str, html_content: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape detailed match information from a VLR.gg match URL or provided HTML.
        """
        try:
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
            else:
                print(f"Fetching HTML from URL: {match_url}")
                response = requests.get(match_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                print("HTML fetched successfully.")

            header_info = self._extract_match_header_info(soup)
            team1_name = header_info.get('team1_name', 'Team 1')
            team2_name = header_info.get('team2_name', 'Team 2')
            
            # If team names are still 'Team 1' or 'N/A', try a fallback
            if team1_name == 'Team 1' or team1_name == 'N/A':
                team_name_elements = soup.select('div.match-header-link-name .wf-title-med')
                if len(team_name_elements) > 0: team1_name = self._safe_get_text(team_name_elements[0])
                if len(team_name_elements) > 1: team2_name = self._safe_get_text(team_name_elements[1])


            match_data = {
                'match_url': match_url,
                'match_id': self._extract_match_id(match_url),
                'scraped_at': datetime.now().isoformat(),
                'event_info': {
                    'name': header_info['event_name'],
                    'stage': header_info['event_stage'],
                    'date_utc': header_info['match_date_utc'],
                    'patch': header_info['patch']
                },
                'teams': {
                    'team1': {'name': team1_name, 'score_overall': header_info['team1_score_overall']},
                    'team2': {'name': team2_name, 'score_overall': header_info['team2_score_overall']}
                },
                'match_format': header_info['match_format'],
                'map_picks_bans_note': header_info['map_picks_bans_note'],
                'maps': self._extract_maps_data(soup, team1_name, team2_name),
                'overall_player_stats': self._extract_overall_player_stats(soup, team1_name, team2_name)
            }
            
            return match_data

        except requests.exceptions.RequestException as e:
            print(f"Network error scraping match details for {match_url}: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error scraping match details for {match_url}: {str(e)}")
            traceback.print_exc()
            return {}

    def create_match_dataframe(self, match_data: Dict) -> pd.DataFrame:
        """Convert match data to pandas DataFrame (simplified example)"""
        all_player_map_stats = []
        for map_info in match_data.get('maps', []):
            for team_name, players in map_info.get('player_stats', {}).items():
                for player_stat in players:
                    flat_stat = {
                        'match_id': match_data.get('match_id'),
                        'map_name': map_info.get('map_name'),
                        'team_name': team_name,
                        'player_name': player_stat.get('player_name'),
                        'agent': player_stat.get('agent'),
                    }
                    flat_stat.update({f"{k}_all": v for k, v in player_stat.get('stats_all_sides', {}).items()})
                    all_player_map_stats.append(flat_stat)
        
        if not all_player_map_stats:
            return pd.DataFrame()
            
        return pd.DataFrame(all_player_map_stats)

def main():
    scraper = MatchDetailsScraper()
    # Use the specific URL requested
    match_url = "https://www.vlr.gg/371266/kr-esports-vs-cloud9-champions-tour-2024-americas-stage-2-ko"
    
    print(f"Attempting to scrape match details from: {match_url}")
    
    # Scrape from the live URL
    match_data = scraper.get_match_details(match_url)

    # --- Uncomment below to test with local HTML file ---
    # html_file_path = r"c:\My Code\Val_Analysis\Project 1\vlr_match_detailed_page.html"
    # print(f"Attempting to load HTML from: {html_file_path}")
    # try:
    #     with open(html_file_path, 'r', encoding='utf-8') as f:
    #         html_content_for_test = f.read()
    #     # Pass the match_url as well, so match_id can be extracted
    #     match_data = scraper.get_match_details(match_url, html_content=html_content_for_test)
    # except FileNotFoundError:
    #     print(f"Error: HTML file not found at {html_file_path}. Ensure the file exists.")
    #     match_data = {} # Ensure match_data is defined
    # except Exception as e:
    #     print(f"Error loading HTML file: {e}")
    #     match_data = {} # Ensure match_data is defined
    # --- End of local HTML test block ---

    if match_data:
        print("\n--- Scraped Match Data ---")
        # Pretty print the JSON to console
        print(json.dumps(match_data, indent=2, ensure_ascii=False))
        
        output_filename = "detailed_match_data.json"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(match_data, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Detailed match data successfully saved to {output_filename}")
        except IOError as e:
            print(f"\n❌ Error saving data to {output_filename}: {e}")

        # Optional: Create and display DataFrame
        # df = scraper.create_match_dataframe(match_data)
        # if not df.empty:
        #     print("\n--- Sample DataFrame (Flattened Player Stats per Map) ---")
        #     print(df.head())
        #     try:
        #         df.to_csv('flattened_match_player_stats.csv', index=False)
        #         print("\n✅ Flattened player stats saved to flattened_match_player_stats.csv")
        #     except IOError as e:
        #         print(f"\n❌ Error saving DataFrame to CSV: {e}")
        # else:
        #     print("\nℹ️ DataFrame is empty, skipping CSV save.")
            
    else:
        print("\n❌ Failed to scrape match details or no data was returned.")

if __name__ == "__main__":
    main()

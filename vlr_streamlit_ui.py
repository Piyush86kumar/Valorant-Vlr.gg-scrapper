import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from vlr_scraper_coordinator import VLRScraperCoordinator
from detailed_match_scraper import DetailedMatchScraper
from vlr_database import VLRDatabase

# Configure Streamlit page
st.set_page_config(
    page_title="VLR.gg Comprehensive Scraper",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_session_state():
    """Initialize session state variables"""
    if 'scraped_data' not in st.session_state:
        st.session_state.scraped_data = None
    if 'scraping_progress' not in st.session_state:
        st.session_state.scraping_progress = 0
    if 'scraping_status' not in st.session_state:
        st.session_state.scraping_status = "Ready to scrape..."
    if 'current_step' not in st.session_state:
        st.session_state.current_step = "idle"
    if 'db' not in st.session_state:
        st.session_state.db = VLRDatabase()
    if 'scraper' not in st.session_state:
        st.session_state.scraper = VLRScraperCoordinator()
    if 'detailed_scraper' not in st.session_state:
        st.session_state.detailed_scraper = DetailedMatchScraper()
    if 'show_data_preview' not in st.session_state:
        st.session_state.show_data_preview = False
    if 'detailed_matches_data' not in st.session_state:
        st.session_state.detailed_matches_data = None

def display_header():
    """Display the main header"""
    st.title("🎮 VLR.gg Event Scraper")
    st.markdown("""
    ### Simple and efficient VLR.gg tournament data extraction

    **Three-step process**:
    1. **🔍 Scrape**: Extract data from VLR.gg event pages
    2. **👁️ Review**: Confirm what data was scraped
    3. **💾 Save**: Choose how to save your data
    """)
    st.divider()

def display_url_input():
    """Display URL input section"""
    st.header("📝 Event URL Input")

    col1, col2 = st.columns([4, 1])

    with col1:
        url = st.text_input(
            "VLR.gg Event URL:",
            placeholder="https://www.vlr.gg/event/2097/valorant-champions-2024",
            help="Enter the main VLR.gg event URL. The scraper will automatically access the matches, stats, and agents tabs.",
            key="main_url"
        )

    with col2:
        st.write("")  # Spacing
        validate_clicked = st.button("🔍 Validate", type="secondary")

    # URL validation
    if validate_clicked and url:
        is_valid, message = st.session_state.scraper.validate_url(url)

        if is_valid:
            st.success(f"✅ {message}")

            # Show constructed URLs
            try:
                # Extract event ID for URL construction
                import re
                match = re.search(r'/event/(\d+)/', url)
                if match:
                    event_id = match.group(1)
                    url_parts = url.split('/')
                    event_name = url_parts[-1] if url_parts[-1] else url_parts[-2]

                    st.info("📋 **URLs that will be scraped:**")
                    st.write(f"🏆 **Matches**: https://www.vlr.gg/event/matches/{event_id}/{event_name}")
                    st.write(f"📊 **Stats**: https://www.vlr.gg/event/stats/{event_id}/{event_name}")
                    st.write(f"🎭 **Agents**: https://www.vlr.gg/event/agents/{event_id}/{event_name}")
            except Exception as e:
                st.warning(f"Could not construct URLs: {e}")
        else:
            st.error(f"❌ {message}")
    elif validate_clicked:
        st.warning("Please enter a URL first")

    return url

def display_control_panel(url):
    """Display simple control panel with scraping options"""
    st.header("🔍 Step 1: Scrape Data")

    col1, col2 = st.columns([3, 1])

    with col1:
        # Simple scraping options
        st.markdown("**Select what to scrape:**")

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            scrape_matches = st.checkbox("🏆 Matches", value=True, help="Match results and scores")
        with col_b:
            scrape_stats = st.checkbox("📊 Player Stats", value=True, help="Individual player performance")
        with col_c:
            scrape_maps_agents = st.checkbox("🎭 Maps & Agents", value=True, help="Agent usage and map data")
        with col_d:
            scrape_detailed_matches = st.checkbox("🔍 Detailed Matches", value=False, help="Comprehensive match details from individual match pages")
            if scrape_detailed_matches:
                max_detailed_matches = st.selectbox(
                    "Max detailed matches to scrape:",
                    [3, 5, 10, 15, 20],
                    index=1,  # Default to 5
                    help="Limit the number of matches to scrape in detail (to avoid long wait times)"
                )

    with col2:
        st.write("")  # Spacing
        scrape_clicked = st.button("🚀 Start Scraping", type="primary",
                                 disabled=not url or st.session_state.current_step == "scraping",
                                 use_container_width=True)

    # Clear data option (smaller)
    if st.session_state.scraped_data:
        if st.button("🗑️ Clear Previous Data", type="secondary"):
            st.session_state.scraped_data = None
            st.session_state.scraping_progress = 0
            st.session_state.scraping_status = "Ready to scrape..."
            st.session_state.current_step = "idle"
            st.rerun()

    # Get max detailed matches if detailed scraping is enabled
    max_detailed = max_detailed_matches if scrape_detailed_matches else 0

    return scrape_clicked, scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed

def display_progress():
    """Display simple scraping progress"""
    if st.session_state.current_step == "scraping":
        st.header("⏳ Scraping in Progress...")

        # Progress bar
        progress_bar = st.progress(st.session_state.scraping_progress / 100)

        # Status text
        status_container = st.container()
        with status_container:
            st.text(st.session_state.scraping_status)

        return status_container

    elif st.session_state.scraped_data:
        st.header("✅ Scraping Completed!")

        # Simple summary
        data = st.session_state.scraped_data
        summary = st.session_state.scraper.get_scraping_summary(data)

        st.success(f"Successfully scraped data for: **{summary['event_title']}**")

        col1, col2, col3 = st.columns(3)
        with col1:
            if summary['total_matches'] > 0:
                st.info(f"🏆 **{summary['total_matches']}** matches found")
        with col2:
            if summary['total_players'] > 0:
                st.info(f"📊 **{summary['total_players']}** players found")
        with col3:
            if summary['total_agents'] > 0:
                st.info(f"🎭 **{summary['total_agents']}** agents found")

        return st.container()

    else:
        return st.container()

def perform_scraping(url, scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches, status_container):
    """Perform the actual scraping using the modular coordinator"""
    try:
        st.session_state.current_step = "scraping"

        # Progress callback function
        def update_progress(message):
            st.session_state.scraping_status = message
            with status_container:
                st.text(message)

        # Validate URL first
        is_valid, message = st.session_state.scraper.validate_url(url)
        if not is_valid:
            st.error(f"❌ {message}")
            st.session_state.current_step = "idle"
            return

        # Initialize progress
        st.session_state.scraping_progress = 10
        update_progress("Initializing modular scrapers...")

        # Use comprehensive scraping with selected modules
        st.session_state.scraping_progress = 20
        update_progress("Starting comprehensive scraping...")

        result = st.session_state.scraper.scrape_comprehensive(
            url,
            scrape_matches=scrape_matches,
            scrape_stats=scrape_stats,
            scrape_maps_agents=scrape_maps_agents,
            progress_callback=update_progress
        )

        # Detailed match scraping if requested
        if scrape_detailed_matches and result.get('matches_data', {}).get('matches'):
            st.session_state.scraping_progress = 80
            update_progress("🔍 Scraping detailed match data...")

            # Extract match URLs
            match_urls = []
            for match in result['matches_data']['matches']:
                match_url = match.get('match_url')
                if match_url:
                    match_urls.append(match_url)

            if match_urls:
                # Limit the number of matches to scrape
                urls_to_scrape = match_urls[:max_detailed_matches]
                update_progress(f"🔍 Found {len(match_urls)} matches, scraping {len(urls_to_scrape)} in detail...")

                # Scrape detailed matches with progress tracking
                detailed_matches = []
                for i, match_url in enumerate(urls_to_scrape):
                    try:
                        update_progress(f"🎯 Scraping detailed match {i+1}/{len(urls_to_scrape)}: {match_url.split('/')[-1]}")
                        match_data = st.session_state.detailed_scraper.scrape_detailed_match(match_url)
                        detailed_matches.append(match_data)

                        # Small delay to avoid overwhelming the server
                        import time
                        time.sleep(1)

                    except Exception as e:
                        update_progress(f"⚠️ Error scraping match {i+1}: {str(e)[:50]}...")
                        continue

                # Store detailed matches data
                st.session_state.detailed_matches_data = detailed_matches

                # Add to result
                result['detailed_matches'] = detailed_matches

                update_progress(f"✅ Scraped {len(detailed_matches)} detailed matches")

        # Complete
        st.session_state.scraping_progress = 100
        st.session_state.scraping_status = "✅ Comprehensive scraping completed successfully!"
        st.session_state.scraped_data = result
        st.session_state.current_step = "completed"

        # Show summary
        summary = st.session_state.scraper.get_scraping_summary(result)
        detailed_count = len(result.get('detailed_matches', []))
        detailed_text = f", {detailed_count} detailed matches" if detailed_count > 0 else ""
        st.success(f"✅ Data scraped successfully! Found {summary['total_matches']} matches, {summary['total_players']} players, {summary['total_agents']} agents{detailed_text}")
        st.rerun()

    except Exception as e:
        st.session_state.scraping_status = f"❌ Error: {str(e)}"
        st.session_state.current_step = "error"
        st.error(f"❌ Error during scraping: {str(e)}")

def display_event_info(event_info):
    """Display event information"""
    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            if 'title' in event_info:
                st.metric("📋 Event Title", event_info['title'])
            if 'dates' in event_info:
                st.metric("📅 Dates", event_info['dates'])

        with col2:
            if 'location' in event_info:
                st.metric("📍 Location", event_info['location'])
            if 'prize_pool' in event_info:
                st.metric("💰 Prize Pool", event_info['prize_pool'])

        if 'description' in event_info:
            st.text_area("📝 Description", event_info['description'], height=100, disabled=True)

        st.text(f"🔗 URL: {event_info['url']}")
        st.text(f"🕒 Scraped: {event_info['scraped_at']}")

def display_matches_data(matches_data):
    """Display matches data with enhanced visualizations"""
    matches = matches_data.get('matches', [])

    if not matches:
        st.warning("No matches data found")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Total Matches", len(matches))

    with col2:
        completed = len([m for m in matches if m.get('status') == 'Completed'])
        st.metric("✅ Completed", completed)

    with col3:
        scheduled = len([m for m in matches if m.get('status') == 'Scheduled'])
        st.metric("⏰ Scheduled", scheduled)

    with col4:
        teams = set()
        for match in matches:
            teams.add(match.get('team1', ''))
            teams.add(match.get('team2', ''))
        teams.discard('')
        st.metric("🏅 Teams", len(teams))

    # Convert to DataFrame for analysis
    matches_df = pd.DataFrame(matches)

    if not matches_df.empty:
        # Matches by stage visualization
        if 'stage' in matches_df.columns:
            st.subheader("📊 Matches by Stage")
            stage_counts = matches_df['stage'].value_counts()

            fig_stages = px.bar(
                x=stage_counts.index,
                y=stage_counts.values,
                title="Number of Matches by Stage",
                labels={'x': 'Stage', 'y': 'Number of Matches'}
            )
            fig_stages.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_stages, use_container_width=True)

        # Team performance analysis for completed matches
        completed_matches = matches_df[matches_df['status'] == 'Completed'].copy()
        if not completed_matches.empty and 'winner' in completed_matches.columns:
            st.subheader("🏆 Team Performance")

            # Calculate wins for each team
            team_wins = {}
            team_matches = {}

            for _, match in completed_matches.iterrows():
                team1, team2 = match.get('team1', ''), match.get('team2', '')
                winner = match.get('winner', '')

                # Initialize teams
                for team in [team1, team2]:
                    if team and team != '':
                        if team not in team_wins:
                            team_wins[team] = 0
                            team_matches[team] = 0
                        team_matches[team] += 1

                # Count wins
                if winner and winner in team_wins:
                    team_wins[winner] += 1

            # Create performance DataFrame
            if team_wins:
                perf_data = []
                for team in team_wins:
                    wins = team_wins[team]
                    total = team_matches[team]
                    win_rate = (wins / total * 100) if total > 0 else 0
                    perf_data.append({
                        'Team': team,
                        'Wins': wins,
                        'Total Matches': total,
                        'Losses': total - wins,
                        'Win Rate (%)': round(win_rate, 1)
                    })

                perf_df = pd.DataFrame(perf_data).sort_values('Win Rate (%)', ascending=False)

                # Display top teams
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**🥇 Top Performing Teams:**")
                    st.dataframe(perf_df.head(10), hide_index=True)

                with col2:
                    # Win rate chart
                    if len(perf_df) > 0:
                        fig_winrate = px.bar(
                            perf_df.head(10),
                            x='Team',
                            y='Win Rate (%)',
                            title="Team Win Rates",
                            color='Win Rate (%)',
                            color_continuous_scale='RdYlGn'
                        )
                        fig_winrate.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_winrate, use_container_width=True)

        # Matches table with filtering
        st.subheader("📋 Matches Table")

        # Add filters
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Filter by Status:",
                options=['All'] + list(matches_df['status'].unique()),
                key="matches_status_filter"
            )

        with col2:
            if 'stage' in matches_df.columns:
                stage_filter = st.selectbox(
                    "Filter by Stage:",
                    options=['All'] + list(matches_df['stage'].unique()),
                    key="matches_stage_filter"
                )
            else:
                stage_filter = 'All'

        with col3:
            # Team search
            team_search = st.text_input(
                "Search Team:",
                placeholder="Enter team name...",
                key="matches_team_search"
            )

        # Apply filters
        filtered_df = matches_df.copy()

        if status_filter != 'All':
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        if stage_filter != 'All' and 'stage' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['stage'] == stage_filter]

        if team_search:
            team_mask = (
                filtered_df['team1'].str.contains(team_search, case=False, na=False) |
                filtered_df['team2'].str.contains(team_search, case=False, na=False)
            )
            filtered_df = filtered_df[team_mask]

        # Display filtered table with all available columns
        display_columns = ['date', 'time', 'team1', 'score', 'team2', 'winner', 'status', 'week', 'stage', 'match_url']
        available_columns = [col for col in display_columns if col in filtered_df.columns]

        st.dataframe(
            filtered_df[available_columns],
            use_container_width=True,
            hide_index=True
        )

        st.info(f"Showing {len(filtered_df)} of {len(matches_df)} matches")

def display_detailed_matches_data(detailed_matches):
    """Display detailed match data in an organized format"""
    if not detailed_matches:
        st.warning("No detailed match data available")
        return

    st.header("🔍 Detailed Match Analysis")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Match Overview", "🎮 Map Details", "👥 Player Performance"])
    
    with tab1:
        st.subheader("Match Summary")
        # Create a DataFrame for match overview
        match_overview = []
        for match in detailed_matches:
            overview = {
                'Match ID': match.get('match_id'),
                'Date': match.get('match_date'),
                'Event': match.get('event_name'),
                'Team 1': match.get('team1_name'),
                'Team 2': match.get('team2_name'),
                'Score': f"{match.get('team1_score')} - {match.get('team2_score')}",
                'Format': match.get('format'),
                'Patch': match.get('patch')
            }
            match_overview.append(overview)
        
        if match_overview:
            df_overview = pd.DataFrame(match_overview)
            st.dataframe(df_overview, use_container_width=True)
    
    with tab2:
        st.subheader("Map Details")
        for match in detailed_matches:
            with st.expander(f"Match {match.get('match_id')}: {match.get('team1_name')} vs {match.get('team2_name')}"):
                for map_data in match.get('maps', []):
                    st.markdown(f"### {map_data.get('map_name')}")
                    st.markdown(f"**Score**: {map_data.get('team1_score')} - {map_data.get('team2_score')}")
                    st.markdown(f"**Picked by**: {map_data.get('pick_team')}")
                    
                    # Display player stats for this map
                    if map_data.get('player_stats'):
                        df_map_stats = pd.DataFrame(map_data['player_stats'])
                        # Remove scraped_at column if it exists
                        if 'scraped_at' in df_map_stats.columns:
                            df_map_stats = df_map_stats.drop('scraped_at', axis=1)
                        st.dataframe(df_map_stats, use_container_width=True)
    
    with tab3:
        st.subheader("Player Performance")
        for match in detailed_matches:
            with st.expander(f"Match {match.get('match_id')}: {match.get('team1_name')} vs {match.get('team2_name')}"):
                # Combine all player stats from all maps
                all_player_stats = []
                for map_data in match.get('maps', []):
                    for player in map_data.get('player_stats', []):
                        player['map'] = map_data.get('map_name')
                        all_player_stats.append(player)
                
                if all_player_stats:
                    df_player_stats = pd.DataFrame(all_player_stats)
                    # Remove the 'scraped_at' column if it exists
                    if 'scraped_at' in df_player_stats.columns:
                        df_player_stats = df_player_stats.drop('scraped_at', axis=1)
                    st.dataframe(df_player_stats, use_container_width=True)

def display_stats_data(stats_data):
    """Display player statistics data with enhanced visualizations"""
    player_stats = stats_data.get('player_stats', [])

    if not player_stats:
        st.warning("No player statistics found")
        return

    # Convert to DataFrame
    stats_df = pd.DataFrame(player_stats)

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("👥 Total Players", len(player_stats))

    with col2:
        unique_teams = len(set([p.get('team', '') for p in player_stats if p.get('team')]))
        st.metric("🏅 Teams", unique_teams)

    with col3:
        # Average ACS
        if 'acs' in stats_df.columns:
            avg_acs = pd.to_numeric(stats_df['acs'], errors='coerce').mean()
            st.metric("📊 Avg ACS", f"{avg_acs:.1f}" if not pd.isna(avg_acs) else "N/A")
        else:
            st.metric("📊 Data Points", len(player_stats))

    with col4:
        # Average K/D
        if 'kd_ratio' in stats_df.columns:
            kd_numeric = pd.to_numeric(stats_df['kd_ratio'], errors='coerce')
            avg_kd = kd_numeric.mean()
            st.metric("⚔️ Avg K/D", f"{avg_kd:.2f}" if not pd.isna(avg_kd) else "N/A")
        else:
            st.metric("📈 Records", len(player_stats))

    # Convert numeric columns for analysis
    numeric_cols = ['rating', 'acs', 'kills', 'deaths', 'assists', 'adr', 'kd_ratio']
    for col in numeric_cols:
        if col in stats_df.columns:
            stats_df[col] = pd.to_numeric(stats_df[col], errors='coerce')

    # Top performers section
    st.subheader("🌟 Top Performers")

    # Create tabs for different metrics
    perf_tab1, perf_tab2, perf_tab3, perf_tab4 = st.tabs(["🎯 ACS Leaders", "⚔️ K/D Leaders", "🔥 Fraggers", "🎖️ Rating Leaders"])

    with perf_tab1:
        if 'acs' in stats_df.columns:
            top_acs = stats_df.nlargest(15, 'acs')[['player', 'team', 'acs', 'kills', 'deaths', 'kd_ratio']]

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(top_acs.head(10), hide_index=True)

            with col2:
                # ACS distribution chart
                fig_acs = px.bar(
                    top_acs.head(10),
                    x='player',
                    y='acs',
                    title="Top 10 Players by ACS",
                    color='acs',
                    color_continuous_scale='viridis'
                )
                fig_acs.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_acs, use_container_width=True)

    with perf_tab2:
        if 'kd_ratio' in stats_df.columns:
            # Filter out infinite values for display
            kd_filtered = stats_df[stats_df['kd_ratio'] != float('inf')].copy()
            top_kd = kd_filtered.nlargest(15, 'kd_ratio')[['player', 'team', 'kd_ratio', 'kills', 'deaths', 'acs']]

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(top_kd.head(10), hide_index=True)

            with col2:
                # K/D scatter plot
                if len(top_kd) > 0:
                    fig_kd = px.scatter(
                        top_kd.head(15),
                        x='kills',
                        y='deaths',
                        size='kd_ratio',
                        color='kd_ratio',
                        hover_data=['player', 'team'],
                        title="Kills vs Deaths (Size = K/D Ratio)",
                        color_continuous_scale='RdYlGn'
                    )
                    st.plotly_chart(fig_kd, use_container_width=True)

    with perf_tab3:
        if 'kills' in stats_df.columns:
            top_kills = stats_df.nlargest(15, 'kills')[['player', 'team', 'kills', 'deaths', 'acs', 'kd_ratio']]

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(top_kills.head(10), hide_index=True)

            with col2:
                # Kills distribution
                fig_kills = px.histogram(
                    stats_df,
                    x='kills',
                    nbins=20,
                    title="Distribution of Kills",
                    labels={'count': 'Number of Players'}
                )
                st.plotly_chart(fig_kills, use_container_width=True)

    with perf_tab4:
        if 'rating' in stats_df.columns:
            top_rating = stats_df.nlargest(15, 'rating')[['player', 'team', 'rating', 'acs', 'kills', 'kd_ratio']]

            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(top_rating.head(10), hide_index=True)

            with col2:
                # Rating vs ACS correlation
                if len(stats_df) > 0:
                    fig_rating = px.scatter(
                        stats_df.head(50),
                        x='rating',
                        y='acs',
                        hover_data=['player', 'team'],
                        title="Rating vs ACS Correlation",
                        trendline="ols"
                    )
                    st.plotly_chart(fig_rating, use_container_width=True)

    # Team analysis
    if 'team' in stats_df.columns and stats_df['team'].notna().any():
        st.subheader("🏅 Team Analysis")

        # Calculate team averages
        team_stats = stats_df.groupby('team').agg({
            'acs': 'mean',
            'kd_ratio': 'mean',
            'kills': 'mean',
            'rating': 'mean'
        }).round(2)

        team_stats['player_count'] = stats_df.groupby('team').size()
        team_stats = team_stats.sort_values('acs', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            st.write("**📊 Team Performance Summary:**")
            st.dataframe(team_stats, use_container_width=True)

        with col2:
            # Team ACS comparison
            if len(team_stats) > 0:
                fig_team = px.bar(
                    team_stats.head(10),
                    y=team_stats.head(10).index,
                    x='acs',
                    orientation='h',
                    title="Team Average ACS",
                    color='acs',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_team, use_container_width=True)

    # Player search and filtering
    st.subheader("🔍 Player Search & Filter")

    col1, col2, col3 = st.columns(3)

    with col1:
        player_search = st.text_input(
            "Search Player:",
            placeholder="Enter player name...",
            key="player_search"
        )

    with col2:
        if 'team' in stats_df.columns:
            team_filter = st.selectbox(
                "Filter by Team:",
                options=['All'] + sorted(stats_df['team'].dropna().unique().tolist()),
                key="player_team_filter"
            )
        else:
            team_filter = 'All'

    with col3:
        # Sort options
        sort_options = ['acs', 'rating', 'kills', 'kd_ratio', 'adr']
        available_sort = [opt for opt in sort_options if opt in stats_df.columns]

        if available_sort:
            sort_by = st.selectbox(
                "Sort by:",
                options=available_sort,
                key="player_sort"
            )
        else:
            sort_by = None

    # Apply filters
    filtered_stats = stats_df.copy()

    if player_search:
        filtered_stats = filtered_stats[
            filtered_stats['player'].str.contains(player_search, case=False, na=False)
        ]

    if team_filter != 'All' and 'team' in filtered_stats.columns:
        filtered_stats = filtered_stats[filtered_stats['team'] == team_filter]

    if sort_by and sort_by in filtered_stats.columns:
        filtered_stats = filtered_stats.sort_values(sort_by, ascending=False)

    # Full stats table
    st.subheader("📊 Player Statistics Table")
    display_cols = [
        'player_id', 'player', 'team', 'agents_display', 'rating', 'acs', 'kd_ratio', 'kast', 'adr',
        'kills', 'deaths', 'assists', 'rounds', 'kpr', 'apr',
        'fkpr', 'fdpr', 'hs_percent', 'cl_percent', 'clutches',
        'k_max', 'first_kills', 'first_deaths', 'agents_count'
    ]
    available_cols = [col for col in display_cols if col in filtered_stats.columns]

    st.dataframe(
        filtered_stats[available_cols],
        use_container_width=True,
        hide_index=True
    )

    st.info(f"Showing {len(filtered_stats)} of {len(stats_df)} players")

def display_maps_agents_data(maps_agents_data):
    """Display maps and agents data with visualizations"""
    if not maps_agents_data:
        st.warning("No maps and agents data available")
        return

    st.header("🎭 Maps & Agents Analysis")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["🗺️ Map Statistics", "🎮 Agent Utilization"])
    
    with tab1:
        st.subheader("Map Statistics")
        if 'maps' in maps_agents_data:
            maps_df = pd.DataFrame(maps_agents_data['maps'])
            if not maps_df.empty:
                # Remove scraped_at column if it exists
                if 'scraped_at' in maps_df.columns:
                    maps_df = maps_df.drop('scraped_at', axis=1)
                st.dataframe(maps_df, use_container_width=True)
                
                # Create map win rate visualization
                if 'map_name' in maps_df.columns and 'attack_win_percent' in maps_df.columns:
                    # Convert percentages to numeric values
                    maps_df['attack_win'] = pd.to_numeric(maps_df['attack_win_percent'].str.replace('%', ''), errors='coerce')
                    maps_df['defense_win'] = pd.to_numeric(maps_df['defense_win_percent'].str.replace('%', ''), errors='coerce')
                    
                    # Create the visualization
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        name='Attack Win %',
                        x=maps_df['map_name'],
                        y=maps_df['attack_win']
                    ))
                    fig.add_trace(go.Bar(
                        name='Defense Win %',
                        x=maps_df['map_name'],
                        y=maps_df['defense_win']
                    ))
                    fig.update_layout(
                        title='Map Win Rates by Side',
                        barmode='group',
                        xaxis_title='Map',
                        yaxis_title='Win Rate (%)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Agent Utilization")
        if 'agents' in maps_agents_data:
            agents_df = pd.DataFrame(maps_agents_data['agents'])
            if not agents_df.empty:
                # Remove scraped_at column if it exists
                if 'scraped_at' in agents_df.columns:
                    agents_df = agents_df.drop('scraped_at', axis=1)
                
                # Display total utilization
                st.markdown("### Total Agent Utilization")
                total_util_df = agents_df[['agent_name', 'total_utilization_percent']].copy()
                total_util_df = total_util_df.sort_values('total_utilization_percent', ascending=False)
                st.dataframe(total_util_df, use_container_width=True)
                
                # Create total utilization visualization
                fig = px.bar(total_util_df, 
                           x='agent_name', 
                           y='total_utilization_percent',
                           title='Total Agent Utilization',
                           labels={'agent_name': 'Agent', 'total_utilization_percent': 'Utilization (%)'})
                st.plotly_chart(fig, use_container_width=True)
                
                # Display map-specific utilization
                st.markdown("### Map-Specific Agent Utilization")
                for _, agent in agents_df.iterrows():
                    with st.expander(f"{agent['agent_name']} - {agent['total_utilization_percent']}% Total"):
                        if agent.get('map_utilizations'):
                            map_utils = pd.DataFrame(agent['map_utilizations'])
                            map_utils = map_utils.sort_values('utilization_percent', ascending=False)
                            
                            # Create map-specific visualization
                            fig = px.bar(map_utils,
                                       x='map',
                                       y='utilization_percent',
                                       title=f"{agent['agent_name']} Map Utilization",
                                       labels={'map': 'Map', 'utilization_percent': 'Utilization (%)'})
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Display the data table
                            st.dataframe(map_utils, use_container_width=True)

def display_simple_data_preview():
    """Display complete data preview for confirmation"""
    if not st.session_state.scraped_data:
        return

    st.header("👁️ Step 2: Review Scraped Data")
    data = st.session_state.scraped_data

    # Event info
    event_info = data.get('event_info', {})
    if event_info:
        st.subheader("📋 Event Information")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {event_info.get('title', 'N/A')}")
                st.write(f"**Dates:** {event_info.get('dates', 'N/A')}")
            with col2:
                st.write(f"**Location:** {event_info.get('location', 'N/A')}")
                st.write(f"**Prize Pool:** {event_info.get('prize_pool', 'N/A')}")

    # Matches data - show all
    matches_data = data.get('matches_data', {})
    if matches_data and matches_data.get('matches'):
        st.subheader("🏆 Matches Data")
        matches = matches_data['matches']

        with st.container(border=True):
            st.write(f"**Total matches found:** {len(matches)}")

            # Show all matches in a table
            if matches:
                matches_df = pd.DataFrame(matches)
                display_columns = ['date', 'time', 'team1', 'score', 'team2', 'winner', 'status', 'week', 'stage', 'match_url']
                available_columns = [col for col in display_columns if col in matches_df.columns]

                st.dataframe(
                    matches_df[available_columns],
                    use_container_width=True,
                    hide_index=True
                )

    # Detailed matches data - show all, RAW, no summary, no aggregation, all columns/rows, no match duration
    detailed_matches = data.get('detailed_matches', [])
    if detailed_matches:
        st.subheader("🔍 Detailed Matches Data (Raw)")
        st.info("Below is the exact, raw detailed match data as scraped. All columns and rows are shown, with no aggregation, filtering, or match duration. Please review before saving.")
        for i, match in enumerate(detailed_matches):
            with st.expander(f"Match {i+1}: {match.get('team1_name', 'Team 1')} vs {match.get('team2_name', 'Team 2')}", expanded=i==0):
                st.write(f"**Match ID:** {match.get('match_id', 'N/A')}")
                st.write(f"**Teams:** {match.get('team1_name', 'N/A')} vs {match.get('team2_name', 'N/A')}")
                st.write(f"**Score:** {match.get('team1_score', 0)}:{match.get('team2_score', 0)}")
                st.write(f"**Status:** {match.get('match_status', 'N/A')}")
                st.write(f"**Maps Played:** {match.get('maps_played', 0)}")
                st.write(f"**Winner:** {match.get('winner_team', 'N/A')}")
                if match.get('match_url'):
                    st.markdown(f"🔗 **[View on VLR.gg]({match.get('match_url')})**")
                # Show the full, raw player_stats DataFrame with all columns
                if match.get('player_stats'):
                    st.markdown("**Raw Player Stats (All Columns, All Rows):**")
                    stats_df = pd.DataFrame(match['player_stats'])
                    st.dataframe(stats_df, use_container_width=True, hide_index=True)

    # Player stats data - show all
    stats_data = data.get('stats_data', {})
    if stats_data and stats_data.get('player_stats'):
        st.subheader("📊 Player Statistics")
        players = stats_data['player_stats']

        with st.container(border=True):
            st.write(f"**Total players found:** {len(players)}")

            # Show all players in a table
            if players:
                players_df = pd.DataFrame(players)
                display_columns = [
                    'player_id', 'player', 'team', 'agents_display', 'rating', 'acs', 'kd_ratio', 'kast', 'adr',
                    'kills', 'deaths', 'assists', 'rounds', 'kpr', 'apr',
                    'fkpr', 'fdpr', 'hs_percent', 'cl_percent', 'clutches',
                    'k_max', 'first_kills', 'first_deaths', 'agents_count'
                ]
                available_columns = [col for col in display_columns if col in players_df.columns]

                st.dataframe(
                    players_df[available_columns],
                    use_container_width=True,
                    hide_index=True
                )

    # Maps & Agents data - show all (updated for new structure)
    maps_agents_data = data.get('maps_agents_data', {})

    # Handle new structure (maps and agents) or old structure (agent_stats and map_stats)
    agents = maps_agents_data.get('agents', maps_agents_data.get('agent_stats', []))
    maps = maps_agents_data.get('maps', maps_agents_data.get('map_stats', []))

    if agents:
        st.subheader("🎭 Agent Utilization Statistics")

        with st.container(border=True):
            st.write(f"**Total agents found:** {len(agents)}")

            agents_df = pd.DataFrame(agents)
            st.dataframe(agents_df, use_container_width=True, hide_index=True)

    if maps:
        st.subheader("🗺️ Map Statistics")

        with st.container(border=True):
            st.write(f"**Total maps found:** {len(maps)}")

            maps_df = pd.DataFrame(maps)
            st.dataframe(maps_df, use_container_width=True, hide_index=True)

def display_database_section():
    """Display database management section"""
    st.header("🗄️ Database Management")

    # Database stats
    db_stats = st.session_state.db.get_database_stats()
    db_size = st.session_state.db.get_database_size()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Events", db_stats.get('total_events', 0))

    with col2:
        st.metric("🏆 Matches", db_stats.get('total_matches', 0))

    with col3:
        st.metric("👥 Players", db_stats.get('unique_players', 0))

    with col4:
        st.metric("💾 DB Size", db_size)

    # Save to database section
    if st.session_state.scraped_data:
        st.subheader("💾 Save Current Data to Database")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🗄️ Save to Database", type="primary"):
                try:
                    event_id = st.session_state.db.save_comprehensive_data(st.session_state.scraped_data)
                    st.success(f"✅ Data saved to database! Event ID: {event_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving to database: {e}")

        with col2:
            st.info("💡 **Tip**: Save your scraped data to the database for persistent storage and easy retrieval later.")

    # View saved events
    st.subheader("📋 Saved Events")

    try:
        events_df = st.session_state.db.get_events_list()

        if not events_df.empty:
            # Display events table
            st.dataframe(
                events_df[['event_id', 'title', 'dates', 'location', 'scraped_at']],
                use_container_width=True,
                hide_index=True
            )

            # Event management
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_event = st.selectbox(
                    "Select Event to View:",
                    options=events_df['event_id'].tolist(),
                    format_func=lambda x: f"{x} - {events_df[events_df['event_id']==x]['title'].iloc[0] if len(events_df[events_df['event_id']==x]) > 0 else 'Unknown'}",
                    key="db_event_select"
                )

            with col2:
                if st.button("👁️ View Event Data"):
                    if selected_event:
                        try:
                            event_data = st.session_state.db.get_event_data(selected_event)
                            st.session_state.db_event_data = event_data
                            st.session_state.show_db_event = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error loading event data: {e}")

            with col3:
                if st.button("🗑️ Delete Event", type="secondary"):
                    if selected_event:
                        if st.session_state.db.delete_event(selected_event):
                            st.success(f"Event {selected_event} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete event")
        else:
            st.info("No events saved in database yet. Scrape some data and save it to get started!")

    except Exception as e:
        st.error(f"Error accessing database: {e}")

def display_database_event_data():
    """Display event data from database"""
    if not hasattr(st.session_state, 'db_event_data') or not st.session_state.get('show_db_event', False):
        return

    st.header("📊 Database Event Data")

    event_data = st.session_state.db_event_data

    # Close button
    if st.button("❌ Close Database View"):
        st.session_state.show_db_event = False
        st.rerun()

    # Create tabs for database data
    tab1, tab2, tab3, tab4 = st.tabs(["ℹ️ Event Info", "🏆 Matches", "📊 Player Stats", "🎭 Agent Usage"])

    with tab1:
        if not event_data['event_info'].empty:
            event_info = event_data['event_info'].iloc[0]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("📋 Title", event_info.get('title', 'N/A'))
                st.metric("📅 Dates", event_info.get('dates', 'N/A'))

            with col2:
                st.metric("📍 Location", event_info.get('location', 'N/A'))
                st.metric("💰 Prize Pool", event_info.get('prize_pool', 'N/A'))
        else:
            st.warning("No event information found")

    with tab2:
        if not event_data['matches'].empty:
            matches_df = event_data['matches']

            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Matches", len(matches_df))
            with col2:
                completed = len(matches_df[matches_df['status'] == 'Completed'])
                st.metric("✅ Completed", completed)
            with col3:
                scheduled = len(matches_df[matches_df['status'] == 'Scheduled'])
                st.metric("⏰ Scheduled", scheduled)

            # Matches table
            display_cols = ['date', 'time', 'team1', 'score', 'team2', 'winner', 'status', 'week', 'stage']
            available_cols = [col for col in display_cols if col in matches_df.columns]

            st.dataframe(
                matches_df[available_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No matches data found")

    with tab3:
        if not event_data['player_stats'].empty:
            stats_df = event_data['player_stats']

            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Players", len(stats_df))
            with col2:
                unique_teams = stats_df['team'].nunique()
                st.metric("🏅 Teams", unique_teams)
            with col3:
                avg_acs = stats_df['acs'].mean() if 'acs' in stats_df.columns else 0
                st.metric("📊 Avg ACS", f"{avg_acs:.1f}")

            # Top performers
            if 'acs' in stats_df.columns:
                top_players = stats_df.nlargest(10, 'acs')[['player', 'team', 'acs', 'kills', 'deaths', 'kd_ratio']]
                st.subheader("🌟 Top Performers")
                st.dataframe(top_players, hide_index=True)

            # Full table
            st.subheader("📊 All Player Statistics")
            display_cols = ['player', 'team', 'rating', 'acs', 'kills', 'deaths', 'kd_ratio']
            available_cols = [col for col in display_cols if col in stats_df.columns]

            st.dataframe(
                stats_df[available_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No player statistics found")

    with tab4:
        if not event_data['agent_usage'].empty:
            agents_df = event_data['agent_usage']

            # Summary
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🎭 Total Agents", len(agents_df))
            with col2:
                total_usage = agents_df['usage_count'].sum() if 'usage_count' in agents_df.columns else 0
                st.metric("📊 Total Picks", total_usage)

            # Agent usage chart
            if 'usage_percentage' in agents_df.columns:
                # Clean percentage data
                agents_df['usage_pct_clean'] = pd.to_numeric(
                    agents_df['usage_percentage'].str.replace('%', ''),
                    errors='coerce'
                )

                fig = px.bar(
                    agents_df.head(10),
                    x='agent',
                    y='usage_pct_clean',
                    title='Agent Usage Distribution',
                    labels={'usage_pct_clean': 'Usage Percentage (%)', 'agent': 'Agent'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            # Full table
            st.subheader("🎭 Agent Usage Statistics")
            display_cols = ['agent', 'usage_count', 'usage_percentage', 'win_rate']
            available_cols = [col for col in display_cols if col in agents_df.columns]

            st.dataframe(
                agents_df[available_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No agent usage data found")

def display_save_options():
    """Display 3 main save options as requested"""
    if not st.session_state.scraped_data:
        return

    st.header("💾 Step 3: Save Your Data")

    st.markdown("Choose how you want to save the scraped data:")

    # 3 main options in columns
    col1, col2, col3 = st.columns(3)

    data = st.session_state.scraped_data

    # Option 1: Save to Database
    with col1:
        st.subheader("🗄️ Save to Database")
        st.markdown("Save all data to SQLite3 database for persistent storage")

        if st.button("💾 Save to Database", type="primary", use_container_width=True):
            try:
                with st.spinner("Saving to database..."):
                    event_id = st.session_state.db.save_comprehensive_data(st.session_state.scraped_data)

                    # Also save detailed matches if available
                    detailed_matches = st.session_state.scraped_data.get('detailed_matches', [])
                    if detailed_matches:
                        detailed_count = st.session_state.db.save_detailed_matches(detailed_matches, event_id)
                        st.success(f"✅ Data saved to database! Event ID: {event_id}")
                        st.info(f"📊 Saved {detailed_count} detailed matches")
                    else:
                        st.success(f"✅ Data saved to database! Event ID: {event_id}")

                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving to database: {e}")

    # Option 2: Download Complete JSON
    with col2:
        st.subheader("📄 Download JSON")
        st.markdown("Download all scraped data in a single JSON file")

        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download Complete JSON",
            data=json_data,
            file_name=f"vlr_complete_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True,
            help="Download all scraped data in JSON format"
        )

    # Option 3: Download CSV Files
    with col3:
        st.subheader("📊 Download CSV")
        st.markdown("Download data as separate CSV files by category")

        # Main CSV download button (combined data)
        if st.button("📊 Download CSV Files", type="secondary", use_container_width=True):
            st.info("👇 Use the additional download options below to get specific CSV files")

    st.divider()

    # Additional CSV download options
    with st.expander("📁 Additional CSV Download Options", expanded=True):
        st.markdown("**Download specific data categories as CSV files:**")

        # Check if we have detailed matches to show 5 columns instead of 4
        has_detailed_matches = bool(data.get('detailed_matches'))
        if has_detailed_matches:
            col1, col2, col3, col4, col5 = st.columns(5)
        else:
            col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Matches CSV
            if data.get('matches_data', {}).get('matches'):
                matches_df = pd.DataFrame(data['matches_data']['matches'])
                matches_csv = matches_df.to_csv(index=False)
                st.download_button(
                    label="🏆 Matches CSV",
                    data=matches_csv,
                    file_name=f"vlr_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download matches data as CSV",
                    use_container_width=True
                )
            else:
                st.info("No matches data")

        with col2:
            # Player stats CSV
            if data.get('stats_data', {}).get('player_stats'):
                stats_df = pd.DataFrame(data['stats_data']['player_stats'])
                stats_csv = stats_df.to_csv(index=False)
                st.download_button(
                    label="📊 Player Stats CSV",
                    data=stats_csv,
                    file_name=f"vlr_player_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download player statistics as CSV",
                    use_container_width=True
                )
            else:
                st.info("No player stats data")

        with col3:
            # Agent utilization CSV
            maps_agents_data = data.get('maps_agents_data', {})
            agents = maps_agents_data.get('agents', maps_agents_data.get('agent_stats', []))

            if agents:
                # Create VLR.gg style table for CSV
                vlr_table_data = []
                for agent in agents:
                    row_data = {
                        'Agent': agent.get('agent_name', agent.get('agent', 'Unknown')),
                        'Total': agent.get('total_utilization_percent', agent.get('average_utilization_percent', 0))
                    }

                    # Add individual map utilizations
                    map_utils = agent.get('map_utilizations', [])
                    for map_util in map_utils:
                        map_name = map_util.get('map', '')
                        utilization = map_util.get('utilization_percent', 0)
                        row_data[map_name] = utilization

                    vlr_table_data.append(row_data)

                if vlr_table_data:
                    agents_df = pd.DataFrame(vlr_table_data)
                    agents_csv = agents_df.to_csv(index=False)
                    st.download_button(
                        label="🎭 Agent Utilization CSV",
                        data=agents_csv,
                        file_name=f"vlr_agent_utilization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download agent utilization data as CSV",
                        use_container_width=True
                    )
                else:
                    st.info("No agent utilization data")
            else:
                st.info("No agent data")

        with col4:
            # Maps CSV
            maps = maps_agents_data.get('maps', maps_agents_data.get('map_stats', []))

            if maps:
                maps_df = pd.DataFrame(maps)
                maps_csv = maps_df.to_csv(index=False)
                st.download_button(
                    label="🗺️ Maps CSV",
                    data=maps_csv,
                    file_name=f"vlr_maps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download maps data as CSV",
                    use_container_width=True
                )
            else:
                st.info("No maps data")

        # Detailed matches CSV (only if available)
        if has_detailed_matches:
            with col5:
                detailed_matches = data.get('detailed_matches', [])
                if detailed_matches:
                    # Convert detailed matches to CSV format
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

                    if detailed_csv_data:
                        detailed_df = pd.DataFrame(detailed_csv_data)
                        detailed_csv = detailed_df.to_csv(index=False)
                        st.download_button(
                            label="🔍 Detailed Matches CSV",
                            data=detailed_csv,
                            file_name=f"vlr_detailed_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="Download detailed match data as CSV",
                            use_container_width=True
                        )
                    else:
                        st.info("No detailed matches data")
                else:
                    st.info("No detailed matches")


def display_example_urls():
    """Display example URLs"""
    st.header("📝 Example URLs")
    st.markdown("""
    Here are some example VLR.gg event URLs you can use:
    """)

    examples = [
        ("Valorant Champions 2024", "https://www.vlr.gg/event/2097/valorant-champions-2024"),
        ("Masters Madrid 2024", "https://www.vlr.gg/event/1921/champions-tour-2024-masters-madrid"),
        ("Masters Shanghai 2024", "https://www.vlr.gg/event/1999/champions-tour-2024-masters-shanghai"),
    ]

    for title, url in examples:
        st.code(f"{title}: {url}")

def main():
    """Main Streamlit application"""
    # Initialize session state
    init_session_state()

    # Sidebar for navigation
    with st.sidebar:
        st.title("🎮 VLR Scraper")

        page = st.radio(
            "Navigate to:",
            ["🔍 Scrape Data", "🗄️ Database", "📊 View Database Event"],
            key="navigation"
        )

        # Database quick stats in sidebar
        st.divider()
        st.subheader("📊 Database Stats")
        try:
            db_stats = st.session_state.db.get_database_stats()
            st.metric("Events", db_stats.get('total_events', 0))
            st.metric("Matches", db_stats.get('total_matches', 0))
            st.metric("Players", db_stats.get('unique_players', 0))
        except:
            st.error("Database connection issue")

    # Main content based on navigation
    if page == "🔍 Scrape Data":
        # Display header
        display_header()

        # URL input section
        url = display_url_input()
        st.divider()

        # Control panel
        scrape_clicked, scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches = display_control_panel(url)
        st.divider()

        # Progress section
        status_container = display_progress()
        st.divider()

        # Handle scraping
        if scrape_clicked and url:
            perform_scraping(url, scrape_matches, scrape_stats, scrape_maps_agents, scrape_detailed_matches, max_detailed_matches, status_container)

        # Display simple data preview if available
        if st.session_state.scraped_data:
            display_simple_data_preview()
            st.divider()

            # Save options
            display_save_options()
            st.divider()

            # Reset button
            if st.button("🔄 Start New Scraping Session", type="secondary"):
                st.session_state.scraped_data = None
                st.session_state.scraping_progress = 0
                st.session_state.scraping_status = "Ready to scrape..."
                st.session_state.current_step = "idle"
                st.rerun()
        else:
            # Show examples when no data
            display_example_urls()

    elif page == "🗄️ Database":
        # Database management page
        display_database_section()

    elif page == "📊 View Database Event":
        # Database event viewer
        display_database_event_data()

        # If no event is being viewed, show database section
        if not st.session_state.get('show_db_event', False):
            st.info("👆 Go to the Database page to select an event to view, or use the navigation above.")
            display_database_section()

if __name__ == "__main__":
    main()

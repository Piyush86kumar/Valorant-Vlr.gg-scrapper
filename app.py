import streamlit as st
import pandas as pd
from match_details_scrapper import MatchDetailsScraper
import plotly.express as px
import plotly.graph_objects as go

def main():
    st.set_page_config(page_title="Valorant Match Analysis", layout="wide")
    
    st.title("Valorant Match Analysis")
    st.write("Enter a VLR.gg match URL to analyze the match details")
    
    # URL input
    match_url = st.text_input("Match URL", "https://www.vlr.gg/371266/kr-esports-vs-cloud9-champions-tour-2024-americas-stage-2-ko")
    
    if st.button("Analyze Match"):
        with st.spinner("Fetching match details..."):
            scraper = MatchDetailsScraper()
            match_data = scraper.get_match_details(match_url)
            
            if match_data:
                # Display match info
                st.header("Match Information")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Teams")
                    st.write(f"Team 1: {match_data['teams']['team1']}")
                    st.write(f"Team 2: {match_data['teams']['team2']}")
                    
                with col2:
                    st.subheader("Score")
                    st.write(f"{match_data['teams']['team1']}: {match_data['score']['team1']}")
                    st.write(f"{match_data['teams']['team2']}: {match_data['score']['team2']}")
                
                # Display match details
                st.header("Match Details")
                st.write(f"Event: {match_data['match_info'].get('event', 'N/A')}")
                st.write(f"Date: {match_data['match_info'].get('date', 'N/A')}")
                st.write(f"Status: {match_data['match_info'].get('status', 'N/A')}")
                
                # Display maps
                st.header("Maps")
                maps_df = pd.DataFrame(match_data['maps'])
                st.dataframe(maps_df)
                
                # Create player stats DataFrame
                df = scraper.create_match_dataframe(match_data)
                
                # Display player stats
                st.header("Player Statistics")
                st.dataframe(df)
                
                # Create visualizations
                st.header("Performance Analysis")
                
                # KDA Ratio
                df['kda'] = (df['kills'].astype(float) + df['assists'].astype(float)) / df['deaths'].astype(float)
                
                # KDA Bar Chart
                fig_kda = px.bar(df, x='player', y='kda', color='team',
                               title='KDA Ratio by Player',
                               labels={'player': 'Player', 'kda': 'KDA Ratio'})
                st.plotly_chart(fig_kda)
                
                # Kills vs Deaths Scatter Plot
                fig_kd = px.scatter(df, x='kills', y='deaths', color='team',
                                  hover_data=['player'],
                                  title='Kills vs Deaths',
                                  labels={'kills': 'Kills', 'deaths': 'Deaths'})
                st.plotly_chart(fig_kd)
                
                # ADR Bar Chart
                fig_adr = px.bar(df, x='player', y='adr', color='team',
                               title='Average Damage per Round (ADR)',
                               labels={'player': 'Player', 'adr': 'ADR'})
                st.plotly_chart(fig_adr)
                
                # Headshot Percentage
                df['hs_percentage'] = df['hs'].astype(float)
                fig_hs = px.bar(df, x='player', y='hs_percentage', color='team',
                              title='Headshot Percentage',
                              labels={'player': 'Player', 'hs_percentage': 'HS%'})
                st.plotly_chart(fig_hs)
                
                # Team Comparison
                st.header("Team Comparison")
                
                # Calculate team averages
                team_stats = df.groupby('team').agg({
                    'kills': 'mean',
                    'deaths': 'mean',
                    'assists': 'mean',
                    'adr': 'mean',
                    'hs': 'mean'
                }).round(2)
                
                st.dataframe(team_stats)
                
                # Team Stats Radar Chart
                fig_radar = go.Figure()
                
                for team in df['team'].unique():
                    team_data = df[df['team'] == team]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[team_data['kills'].mean(),
                           team_data['deaths'].mean(),
                           team_data['assists'].mean(),
                           team_data['adr'].mean(),
                           team_data['hs'].mean()],
                        theta=['Kills', 'Deaths', 'Assists', 'ADR', 'HS%'],
                        name=team,
                        fill='toself'
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, max(df['kills'].max(), df['deaths'].max(),
                                        df['assists'].max(), df['adr'].max(),
                                        df['hs'].max())]
                        )),
                    showlegend=True,
                    title="Team Performance Comparison"
                )
                
                st.plotly_chart(fig_radar)
                
            else:
                st.error("Failed to fetch match details. Please check the URL and try again.")

if __name__ == "__main__":
    main() 
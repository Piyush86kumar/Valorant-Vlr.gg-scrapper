import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class VLRDatabase:
    """
    SQLite database manager for VLR.gg scraped data
    Handles storage and retrieval of event data, matches, player stats, and agent usage
    """
    
    def __init__(self, db_path: str = "vlr_data.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.init_database()
        self.migrate_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    dates TEXT,
                    location TEXT,
                    prize_pool TEXT,
                    description TEXT,
                    url TEXT,
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Matches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    match_id TEXT,
                    team1 TEXT,
                    team2 TEXT,
                    score TEXT,
                    score1 TEXT,
                    score2 TEXT,
                    stage TEXT,
                    week TEXT,
                    date TEXT,
                    time TEXT,
                    match_time TEXT,
                    status TEXT,
                    winner TEXT,
                    match_url TEXT,
                    series_id TEXT,
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (event_id)
                )
            ''')

            # Detailed matches table for comprehensive match data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detailed_matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    match_id TEXT UNIQUE,
                    team1_name TEXT,
                    team2_name TEXT,
                    team1_score INTEGER,
                    team2_score INTEGER,
                    final_score TEXT,
                    match_date TEXT,
                    match_time TEXT,
                    match_date_display TEXT,
                    match_time_utc TEXT,
                    tournament_name TEXT,
                    tournament_stage TEXT,
                    match_format TEXT,
                    match_status TEXT,
                    winner_team TEXT,
                    match_duration TEXT,
                    maps_played INTEGER,
                    calculated_score TEXT,
                    map_details TEXT,
                    team1_players TEXT,
                    team2_players TEXT,
                    match_url TEXT,
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (event_id)
                )
            ''')
            
            # Player stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    player TEXT,
                    team TEXT,
                    rating REAL,
                    acs REAL,
                    kills INTEGER,
                    deaths INTEGER,
                    assists INTEGER,
                    plus_minus INTEGER,
                    adr REAL,
                    hs_percent TEXT,
                    first_kills INTEGER,
                    first_deaths INTEGER,
                    kd_ratio REAL,
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (event_id)
                )
            ''')
            
            # Agent usage table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT,
                    agent TEXT,
                    usage_count INTEGER,
                    usage_percentage TEXT,
                    win_rate TEXT,
                    avg_rating REAL,
                    avg_acs REAL,
                    scraped_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events (event_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_matches_event_id ON matches (event_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_stats_event_id ON player_stats (event_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_usage_event_id ON agent_usage (event_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player_stats_player ON player_stats (player)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_usage_agent ON agent_usage (agent)')
            
            conn.commit()

    def migrate_database(self):
        """Migrate existing database to new schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check current matches table schema
                cursor.execute("PRAGMA table_info(matches)")
                columns = [column[1] for column in cursor.fetchall()]

                # List of new columns to add
                new_columns = [
                    ('match_id', 'TEXT'),
                    ('score', 'TEXT'),
                    ('week', 'TEXT'),
                    ('date', 'TEXT'),
                    ('time', 'TEXT')
                ]

                migration_needed = False
                for col_name, col_type in new_columns:
                    if col_name not in columns:
                        print(f"🔄 Migrating database: Adding {col_name} column to matches table...")
                        cursor.execute(f'ALTER TABLE matches ADD COLUMN {col_name} {col_type}')
                        migration_needed = True

                if migration_needed:
                    # Update existing matches with extracted match_ids
                    cursor.execute('SELECT id, match_url FROM matches WHERE match_url IS NOT NULL AND match_id IS NULL')
                    matches = cursor.fetchall()

                    for match_id, match_url in matches:
                        if match_url:
                            import re
                            match_id_match = re.search(r'/(\d+)/', match_url)
                            if match_id_match:
                                extracted_id = match_id_match.group(1)
                                cursor.execute('UPDATE matches SET match_id = ? WHERE id = ?', (extracted_id, match_id))

                    print("✅ Database migration completed")

                conn.commit()

        except Exception as e:
            print(f"⚠️ Database migration warning: {e}")

    def save_comprehensive_data(self, data: Dict[str, Any]) -> str:
        """
        Save comprehensive scraped data to database
        Returns the event_id for reference
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract event info and generate proper event_id
                event_info = data.get('event_info', {})
                urls = data.get('urls', {})

                # Try multiple ways to get event_id
                event_id = None
                if urls and 'event_id' in urls:
                    event_id = urls['event_id']
                elif event_info and 'url' in event_info:
                    # Extract event_id from URL
                    import re
                    url = event_info['url']
                    match = re.search(r'/event/(\d+)/', url)
                    if match:
                        event_id = match.group(1)

                # Fallback to timestamp-based ID if still unknown
                if not event_id or event_id == 'unknown':
                    event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Save event info
                cursor.execute('''
                    INSERT OR REPLACE INTO events 
                    (event_id, title, dates, location, prize_pool, description, url, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event_id,
                    event_info.get('title'),
                    event_info.get('dates'),
                    event_info.get('location'),
                    event_info.get('prize_pool'),
                    event_info.get('description'),
                    event_info.get('url'),
                    event_info.get('scraped_at')
                ))
                
                # Save matches data
                matches_data = data.get('matches_data', {})
                matches = matches_data.get('matches', [])
                
                # Clear existing matches for this event
                cursor.execute('DELETE FROM matches WHERE event_id = ?', (event_id,))
                
                for match in matches:
                    # Extract match_id from match_url
                    match_id = None
                    match_url = match.get('match_url', '')
                    if match_url:
                        import re
                        match_id_match = re.search(r'/(\d+)/', match_url)
                        if match_id_match:
                            match_id = match_id_match.group(1)

                    cursor.execute('''
                        INSERT INTO matches
                        (event_id, match_id, team1, team2, score, score1, score2, stage, week,
                         date, time, match_time, status, winner, match_url, series_id, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id,
                        match_id,
                        match.get('team1'),
                        match.get('team2'),
                        match.get('score'),
                        match.get('score1'),
                        match.get('score2'),
                        match.get('stage'),
                        match.get('week'),
                        match.get('date'),
                        match.get('time'),
                        match.get('match_time'),
                        match.get('status'),
                        match.get('winner'),
                        match_url,
                        match.get('series_id'),
                        match.get('scraped_at')
                    ))
                
                # Save player stats
                stats_data = data.get('stats_data', {})
                player_stats = stats_data.get('player_stats', [])
                
                # Clear existing player stats for this event
                cursor.execute('DELETE FROM player_stats WHERE event_id = ?', (event_id,))
                
                for player in player_stats:
                    # Convert string numbers to appropriate types
                    rating = self._safe_float(player.get('rating'))
                    acs = self._safe_float(player.get('acs'))
                    kills = self._safe_int(player.get('kills'))
                    deaths = self._safe_int(player.get('deaths'))
                    assists = self._safe_int(player.get('assists'))
                    plus_minus = self._safe_int(player.get('plus_minus'))
                    adr = self._safe_float(player.get('adr'))
                    first_kills = self._safe_int(player.get('first_kills'))
                    first_deaths = self._safe_int(player.get('first_deaths'))
                    kd_ratio = self._safe_float(player.get('kd_ratio'))
                    
                    cursor.execute('''
                        INSERT INTO player_stats 
                        (event_id, player, team, rating, acs, kills, deaths, assists, 
                         plus_minus, adr, hs_percent, first_kills, first_deaths, kd_ratio, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id,
                        player.get('player'),
                        player.get('team'),
                        rating,
                        acs,
                        kills,
                        deaths,
                        assists,
                        plus_minus,
                        adr,
                        player.get('hs_percent'),
                        first_kills,
                        first_deaths,
                        kd_ratio,
                        player.get('scraped_at')
                    ))
                
                # Save agent usage data
                agents_data = data.get('agents_data', {})
                agent_stats = agents_data.get('agent_stats', [])
                
                # Clear existing agent usage for this event
                cursor.execute('DELETE FROM agent_usage WHERE event_id = ?', (event_id,))
                
                for agent in agent_stats:
                    usage_count = self._safe_int(agent.get('usage_count'))
                    avg_rating = self._safe_float(agent.get('avg_rating'))
                    avg_acs = self._safe_float(agent.get('avg_acs'))
                    
                    cursor.execute('''
                        INSERT INTO agent_usage 
                        (event_id, agent, usage_count, usage_percentage, win_rate, 
                         avg_rating, avg_acs, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        event_id,
                        agent.get('agent'),
                        usage_count,
                        agent.get('usage_percentage'),
                        agent.get('win_rate'),
                        avg_rating,
                        avg_acs,
                        agent.get('scraped_at')
                    ))
                
                conn.commit()
                return event_id

        except Exception as e:
            raise Exception(f"Error saving data to database: {e}")

    def save_detailed_match(self, match_data: Dict[str, Any]) -> bool:
        """Save detailed match data to database with validation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Validate required fields
                required_fields = ['match_id', 'team1_name', 'team2_name', 'team1_score', 'team2_score']
                for field in required_fields:
                    if field not in match_data or match_data[field] is None:
                        raise ValueError(f"Missing required field: {field}")
                
                # Clean and prepare data
                match_record = {
                    'match_id': match_data['match_id'],
                    'team1_name': match_data['team1_name'],
                    'team2_name': match_data['team2_name'],
                    'team1_score': self._safe_int(match_data['team1_score']),
                    'team2_score': self._safe_int(match_data['team2_score']),
                    'final_score': match_data.get('final_score', f"{match_data['team1_score']}:{match_data['team2_score']}"),
                    'match_date': match_data.get('match_date'),
                    'match_time': match_data.get('match_time'),
                    'match_date_display': match_data.get('match_date_display'),
                    'match_time_utc': match_data.get('match_time_utc'),
                    'tournament_name': match_data.get('tournament_name'),
                    'tournament_stage': match_data.get('tournament_stage'),
                    'match_format': match_data.get('match_format'),
                    'match_status': match_data.get('match_status'),
                    'winner_team': match_data.get('winner_team'),
                    'match_duration': match_data.get('match_duration'),
                    'maps_played': self._safe_int(match_data.get('maps_played', 0)),
                    'calculated_score': match_data.get('calculated_score'),
                    'map_details': match_data.get('map_details'),
                    'team1_players': match_data.get('team1_players'),
                    'team2_players': match_data.get('team2_players'),
                    'match_url': match_data.get('match_url'),
                    'scraped_at': match_data.get('scraped_at', datetime.now().isoformat())
                }
                
                # Save to database
                cursor.execute('''
                    INSERT OR REPLACE INTO detailed_matches (
                        match_id, team1_name, team2_name, team1_score, team2_score,
                        final_score, match_date, match_time, match_date_display, match_time_utc,
                        tournament_name, tournament_stage, match_format, match_status,
                        winner_team, match_duration, maps_played, calculated_score, map_details,
                        team1_players, team2_players, match_url, scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match_record['match_id'],
                    match_record['team1_name'],
                    match_record['team2_name'],
                    match_record['team1_score'],
                    match_record['team2_score'],
                    match_record['final_score'],
                    match_record['match_date'],
                    match_record['match_time'],
                    match_record['match_date_display'],
                    match_record['match_time_utc'],
                    match_record['tournament_name'],
                    match_record['tournament_stage'],
                    match_record['match_format'],
                    match_record['match_status'],
                    match_record['winner_team'],
                    match_record['match_duration'],
                    match_record['maps_played'],
                    match_record['calculated_score'],
                    match_record['map_details'],
                    match_record['team1_players'],
                    match_record['team2_players'],
                    match_record['match_url'],
                    match_record['scraped_at']
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving detailed match: {e}")
            return False
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None or value == '' or value == 'N/A':
            return None
        try:
            return int(float(str(value)))
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == '' or value == 'N/A':
            return None
        try:
            # Handle percentage strings
            if isinstance(value, str) and '%' in value:
                return float(value.replace('%', ''))
            return float(str(value))
        except (ValueError, TypeError):
            return None
    
    def get_events_list(self) -> pd.DataFrame:
        """Get list of all events in database"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT event_id, title, dates, location, prize_pool, 
                       scraped_at, created_at
                FROM events 
                ORDER BY created_at DESC
            '''
            return pd.read_sql_query(query, conn)
    
    def get_event_data(self, event_id: str) -> Dict[str, pd.DataFrame]:
        """Get all data for a specific event"""
        with sqlite3.connect(self.db_path) as conn:
            data = {}
            
            # Event info
            event_query = 'SELECT * FROM events WHERE event_id = ?'
            data['event_info'] = pd.read_sql_query(event_query, conn, params=(event_id,))
            
            # Matches
            matches_query = 'SELECT * FROM matches WHERE event_id = ? ORDER BY created_at'
            data['matches'] = pd.read_sql_query(matches_query, conn, params=(event_id,))
            
            # Player stats
            stats_query = 'SELECT * FROM player_stats WHERE event_id = ? ORDER BY acs DESC'
            data['player_stats'] = pd.read_sql_query(stats_query, conn, params=(event_id,))
            
            # Agent usage
            agents_query = 'SELECT * FROM agent_usage WHERE event_id = ? ORDER BY usage_count DESC'
            data['agent_usage'] = pd.read_sql_query(agents_query, conn, params=(event_id,))
            
            return data
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count events
            cursor.execute('SELECT COUNT(*) FROM events')
            stats['total_events'] = cursor.fetchone()[0]
            
            # Count matches
            cursor.execute('SELECT COUNT(*) FROM matches')
            stats['total_matches'] = cursor.fetchone()[0]
            
            # Count player records
            cursor.execute('SELECT COUNT(*) FROM player_stats')
            stats['total_player_records'] = cursor.fetchone()[0]
            
            # Count agent records
            cursor.execute('SELECT COUNT(*) FROM agent_usage')
            stats['total_agent_records'] = cursor.fetchone()[0]
            
            # Count unique players
            cursor.execute('SELECT COUNT(DISTINCT player) FROM player_stats')
            stats['unique_players'] = cursor.fetchone()[0]
            
            # Count unique teams
            cursor.execute('SELECT COUNT(DISTINCT team1) FROM matches')
            stats['unique_teams'] = cursor.fetchone()[0]
            
            return stats
    
    def export_to_csv(self, event_id: str, output_dir: str = "exports") -> List[str]:
        """Export event data to CSV files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        data = self.get_event_data(event_id)
        files_created = []
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for table_name, df in data.items():
            if not df.empty:
                filename = f"{output_dir}/{table_name}_{event_id}_{timestamp}.csv"
                df.to_csv(filename, index=False)
                files_created.append(filename)
        
        return files_created
    
    def delete_event(self, event_id: str) -> bool:
        """Delete all data for a specific event"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete in reverse order of dependencies
                cursor.execute('DELETE FROM agent_usage WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM player_stats WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM matches WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM events WHERE event_id = ?', (event_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error deleting event {event_id}: {e}")
            return False
    
    def get_database_size(self) -> str:
        """Get database file size in human readable format"""
        try:
            size_bytes = os.path.getsize(self.db_path)
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            
            return f"{size_bytes:.1f} TB"
            
        except OSError:
            return "Unknown"


# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    db = VLRDatabase("test_vlr_data.db")
    
    print("🗄️ VLR Database Manager Test")
    print("=" * 40)
    
    # Test database initialization
    print("✅ Database initialized successfully")
    
    # Get database stats
    stats = db.get_database_stats()
    print(f"📊 Database Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Get database size
    size = db.get_database_size()
    print(f"💾 Database size: {size}")
    
    # List events
    events_df = db.get_events_list()
    print(f"📋 Events in database: {len(events_df)}")
    
    print("\n✅ Database manager is working correctly!")

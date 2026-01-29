import sqlite3
import json
import os
from typing import List, Dict, Optional

DB_FILE = "data/app.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        directory = os.path.dirname(self.db_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Players table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')
            
            # Matches table (storing full match object as JSON for flexibility)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
            ''')
            
            # Session table (key-value store for session state)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            conn.commit()

    # --- Generic Methods ---
    def execute_query(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_all(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def fetch_one(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    # --- Players ---
    def get_all_players(self) -> List[Dict]:
        rows = self.fetch_all("SELECT id, name FROM players")
        return [{'id': row[0], 'name': row[1]} for row in rows]

    def save_player(self, player: Dict):
        self.execute_query(
            "INSERT OR REPLACE INTO players (id, name) VALUES (?, ?)",
            (player['id'], player['name'])
        )

    def bulk_save_players(self, players: List[Dict]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players") # Replace all strategy for simpler sync
            data = [(p['id'], p['name']) for p in players]
            cursor.executemany("INSERT INTO players (id, name) VALUES (?, ?)", data)
            conn.commit()

    # --- Matches ---
    def get_all_matches(self) -> List[Dict]:
        rows = self.fetch_all("SELECT data FROM matches")
        return [json.loads(row[0]) for row in rows]

    def save_matches(self, matches: List[Dict]):
        # Full replace or append? Context suggests append mostly, but specific saving might be better.
        # For compatibility with current load/save architecture which saves whole list:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM matches")
            data = [(m.get('id', str(i)), json.dumps(m)) for i, m in enumerate(matches)] 
            # Note: matches might not have ID in current JSON, need to check data structure. 
            # If no ID, generate one or use index.
            cursor.executemany("INSERT INTO matches (id, data) VALUES (?, ?)", data)
            conn.commit()

    # --- Session ---
    def get_session(self) -> Optional[Dict]:
        row = self.fetch_one("SELECT value FROM session WHERE key = 'current_session'")
        if row:
            return json.loads(row[0])
        return None

    def save_session(self, session: Dict):
        ensure_teams_have_groups(session)
        self.execute_query(
            "INSERT OR REPLACE INTO session (key, value) VALUES (?, ?)",
            ('current_session', json.dumps(session))
        )

    def clear_session(self):
        self.execute_query("DELETE FROM session WHERE key = 'current_session'")

# Helper to ensure data integrity during save (migrated from logic if needed)
def ensure_teams_have_groups(session):
    if session and 'teams' in session:
        for i, team in enumerate(session['teams']):
            if 'group' not in team:
                team['group'] = 'Group 2' if i >= 6 else 'Group 1'

db = DatabaseManager()

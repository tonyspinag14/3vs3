import json
import os
import shutil
import pandas as pd
from typing import List, Dict
from utils.database import db, DB_FILE

DATA_DIR = "data"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches_history.json")
SESSION_FILE = os.path.join(DATA_DIR, "current_session.json")

def ensure_data_dir():
    # Only ensures directory exists, file creation handled by DB or migration
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def migrate_json_to_db_if_needed():
    """Migrate legacy JSON data to SQLite if DB is empty and JSON exists."""
    # Check if DB has players (proxy for initialized)
    players = db.get_all_players()
    if not players and os.path.exists(PLAYERS_FILE):
        try:
            with open(PLAYERS_FILE, 'r') as f:
                legacy_players = json.load(f)
            if legacy_players:
               db.bulk_save_players(legacy_players)
               print("Migrated players from JSON to DB.")
        except Exception as e:
            print(f"Migration error (Players): {e}")

    # Check matches
    matches = db.get_all_matches()
    if not matches and os.path.exists(MATCHES_FILE):
        try:
            with open(MATCHES_FILE, 'r') as f:
                legacy_matches = json.load(f)
            if legacy_matches:
                db.save_matches(legacy_matches)
                print("Migrated matches from JSON to DB.")
        except Exception as e:
            print(f"Migration error (Matches): {e}")

    # Check session
    session = db.get_session()
    if not session and os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r') as f:
                legacy_session = json.load(f)
            if legacy_session:
                db.save_session(legacy_session)
                print("Migrated session from JSON to DB.")
        except Exception as e:
            print(f"Migration error (Session): {e}")

# Run migration on module load (simple check)
ensure_data_dir()
migrate_json_to_db_if_needed()

def load_players() -> List[Dict]:
    return db.get_all_players()

def save_players(players: List[Dict]):
    db.bulk_save_players(players)

def load_matches_history() -> List[Dict]:
    return db.get_all_matches()

def save_matches_history(matches: List[Dict]):
    db.save_matches(matches)

def load_current_session() -> Dict:
    return db.get_session()

def save_current_session(session: Dict):
    db.save_session(session)

def clear_current_session():
    db.clear_session()

def get_db_binary():
    """Return database file bytes for download."""
    with open(DB_FILE, 'rb') as f:
        return f.read()

def restore_db_from_binary(file_bytes):
    """Overwrite database file with provided bytes."""
    with open(DB_FILE, 'wb') as f:
        f.write(file_bytes)
    # Re-init migration check or reload not strictly needed as next DB call reads file


def calculate_leaderboard(players: List[Dict], matches: List[Dict]) -> pd.DataFrame:
    # Initialize stats for all players
    stats = {p['id']: {'Name': p['name'], 'Pts': 0, 'GP': 0, 'W': 0, 'D': 0, 'L': 0, 'GD': 0} for p in players}
    
    # Process matches
    for m in matches:
        if not m.get('is_complete', False):
            continue
            
        team_a_ids = m['team_a_players']
        team_b_ids = m['team_b_players']
        score_a = int(m['score_a'])
        score_b = int(m['score_b'])
        
        # Determine result
        if score_a > score_b:
            res_a, res_b = 'W', 'L'
            pts_a, pts_b = 3, 0
        elif score_a < score_b:
            res_a, res_b = 'L', 'W'
            pts_a, pts_b = 0, 3
        else:
            res_a, res_b = 'D', 'D'
            pts_a, pts_b = 1, 1
            
        gd_a = score_a - score_b
        gd_b = score_b - score_a
        
        # Update stats for Team A players
        for pid in team_a_ids:
            if pid in stats:
                stats[pid]['GP'] += 1
                stats[pid]['GD'] += gd_a
                stats[pid]['Pts'] += pts_a
                if res_a == 'W': stats[pid]['W'] += 1
                elif res_a == 'D': stats[pid]['D'] += 1
                else: stats[pid]['L'] += 1
                
        # Update stats for Team B players
        for pid in team_b_ids:
            if pid in stats:
                stats[pid]['GP'] += 1
                stats[pid]['GD'] += gd_b
                stats[pid]['Pts'] += pts_b
                if res_b == 'W': stats[pid]['W'] += 1
                elif res_b == 'D': stats[pid]['D'] += 1
                else: stats[pid]['L'] += 1

    df = pd.DataFrame(stats.values())
    if not df.empty:
        # Sort desc by Pts, GD, W
        df = df.sort_values(by=['Pts', 'GD', 'W'], ascending=False).reset_index(drop=True)
        df.index += 1 # Rank starts at 1
    return df

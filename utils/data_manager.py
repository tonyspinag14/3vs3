import json
import os
import pandas as pd
from typing import List, Dict

DATA_DIR = "data"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
MATCHES_FILE = os.path.join(DATA_DIR, "matches_history.json")
SESSION_FILE = os.path.join(DATA_DIR, "current_session.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'w') as f:
            json.dump([], f)
            
    if not os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, 'w') as f:
            json.dump([], f)

def load_players() -> List[Dict]:
    ensure_data_dir()
    with open(PLAYERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_players(players: List[Dict]):
    ensure_data_dir()
    with open(PLAYERS_FILE, 'w') as f:
        json.dump(players, f, indent=2)

def load_matches_history() -> List[Dict]:
    ensure_data_dir()
    with open(MATCHES_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def save_matches_history(matches: List[Dict]):
    ensure_data_dir()
    with open(MATCHES_FILE, 'w') as f:
        json.dump(matches, f, indent=2)

def load_current_session() -> Dict:
    ensure_data_dir()
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return None

def save_current_session(session: Dict):
    ensure_data_dir()
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f, indent=2)

def clear_current_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

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

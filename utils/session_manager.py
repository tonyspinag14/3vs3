import random
import uuid
from typing import List, Dict

def create_teams_empty(num_teams=12) -> List[Dict]:
    """
    Creates empty team skeletons for manual assignment.
    """
    teams = []
    for i in range(num_teams):
        teams.append({
            'id': str(uuid.uuid4()),
            'name': f"Team {i+1}",
            'players': [],
            'player_names': [],
            'group': 'Group 1' if i < (num_teams // 2) else 'Group 2'
        })
    return teams

def init_match_slots(rounds=3, matches_per_round=6) -> List[Dict]:
    """
    Creates empty slots for manual matchmaking.
    Defaults to 2 Groups * 3 Rounds * 6 Matches = 36 Match slots.
    """
    slots = []
    groups = ['Group 1', 'Group 2']
    
    for group in groups:
        for r in range(1, rounds + 1):
            for m in range(1, matches_per_round + 1):
                slots.append({
                    'id': str(uuid.uuid4()),
                    'group': group,
                    'round': r,
                    'match_num': m,
                    'team_a_id': None,
                    'team_b_id': None,
                    'score_a': 0,
                    'score_b': 0,
                    'is_complete': False
                })
    return slots

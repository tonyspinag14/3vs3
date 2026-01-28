
import json
import uuid
import sys
import os

# Add project root to sys path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import data_manager

def add_missing_teams():
    print("Loading session...")
    session = data_manager.load_current_session()
    if not session:
        print("No session.")
        return

    teams = session.get('teams', [])
    current_count = len(teams)
    print(f"Current teams: {current_count}")
    
    if current_count >= 12:
        print("Already have 12 or more teams.")
        return

    # Add teams 7 to 12
    for i in range(current_count, 12):
        team_num = i + 1
        new_team = {
            'id': str(uuid.uuid4()),
            'name': f"Team {team_num}",
            'players': [],
            'player_names': [],
            'group': 'Group 2' # Teams 7-12 go to Group 2
        }
        teams.append(new_team)
        print(f"Added {new_team['name']} ({new_team['group']})")
        
    session['teams'] = teams
    data_manager.save_current_session(session)
    print("Session updated successfully.")

if __name__ == "__main__":
    add_missing_teams()

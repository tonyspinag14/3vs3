import streamlit as st
import uuid
from utils import data_manager, session_manager

def render_setup():
    st.header("🛠 Setup & Team Generation")
    
    # --- Part 1: Player Pool ---
    st.subheader("1. Player Pool")
    
    players = data_manager.load_players()
    
    with st.form("add_player"):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_name = st.text_input("Player Name")
        with col2:
            submitted = st.form_submit_button("Add")
            
        if submitted and new_name:
            players.append({'id': str(uuid.uuid4()), 'name': new_name})
            data_manager.save_players(players)
            st.rerun()

    if players:
        st.caption(f"Total Players: {len(players)}")
        with st.expander("Show Player List"):
            edited_df = st.data_editor(
                players,
                hide_index=True,
                column_config={
                    "id": None, # Hide ID
                    "name": st.column_config.TextColumn("Name", required=True)
                },
                key="player_editor"
            )
            
            # Check for changes
            # Convert back to list of dicts to compare or just save if different
            if edited_df != players:
                 # Update players list
                 data_manager.save_players(edited_df)
                 st.rerun()
            
    st.divider()
    
    # --- Part 2: Session Management ---
    st.subheader("2. Create Teams")
    
    current_session = data_manager.load_current_session()
    
    col_reset, col_create = st.columns([1, 1])
    
    # If no session, Create one
    if not current_session:
        with col_create:
            if st.button("Start New Session (12 Empty Teams)", type="primary"):
                teams = session_manager.create_teams_empty(num_teams=12)
                matches = session_manager.init_match_slots(rounds=3, matches_per_round=6)
                session = {
                    'teams': teams,
                    'matches': matches,
                    'is_active': True
                }
                data_manager.save_current_session(session)
                st.rerun()
    else:
        with col_reset:
            if st.button("⚠ Reset Session (Clear Teams)", type="secondary"):
                data_manager.clear_current_session()
                st.rerun()

    # --- Part 3: Manual Assignment ---
    if current_session:
        st.success("Session Active - Assign Players below")
        
        teams = current_session['teams']
        player_options = {p['name']: p['id'] for p in players}
        player_names_list = list(player_options.keys())
        
        updated = False
        
        # Grid layout for 12 teams
        # 4 columns x 3 rows? Or 3 cols x 4 rows.
        cols = st.columns(3)
        
        for i, team in enumerate(teams):
            with cols[i % 3]:
                with st.container(border=True):
                    # Header: Name + Group Toggle
                    c_head, c_grp = st.columns([2, 1])
                    with c_head:
                        st.markdown(f"**{team['name']}**")
                    with c_grp:
                         current_grp = team.get('group', 'Group 1')
                         # Simple toggle via radio horizontal
                         new_grp = st.radio("Grp", ['Group 1', 'Group 2'], 
                                          index=0 if current_grp == 'Group 1' else 1,
                                          key=f"grp_{team['id']}",
                                          label_visibility="collapsed",
                                          horizontal=True)
                         if new_grp != current_grp:
                             team['group'] = new_grp
                             updated = True
                    
                    # Player Multiselect
                    # Get currently assigned names
                    current_assigned_ids = team['players']
                    # Translate to names for default
                    default_names = []
                    for pid in current_assigned_ids:
                        name = next((p['name'] for p in players if p['id'] == pid), None)
                        if name: default_names.append(name)
                        
                    selected_names = st.multiselect("Players", player_names_list, 
                                                    default=default_names,
                                                    key=f"team_{team['id']}_sel",
                                                    label_visibility="collapsed")
                    
                    # Update if changed
                    # Convert names back to IDs
                    new_ids = [player_options[n] for n in selected_names]
                    if set(new_ids) != set(current_assigned_ids):
                         team['players'] = new_ids
                         team['player_names'] = selected_names
                         updated = True
                         
        if updated:
            data_manager.save_current_session(current_session)
            # st.rerun() # Rerun might interpret input flow, sometimes better to let user finish. 
            # But multiselect sync is tricky. Streamlit executes script top-down. 
            # If we updated the object in memory, we should save it.
            # Next rerun will load it.

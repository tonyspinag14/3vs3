import streamlit as st
from utils import data_manager

def render_matches():
    st.header("⚽ Matches")
    
    session = data_manager.load_current_session()
    if not session:
        st.info("No active session. Go to Setup to start.")
        return

    teams = session['teams']
    matches = session['matches']
    
    # Team Options for Dropdown: Format "Name (Group)"
    # Filter teams that have players? No, allow all.
    team_options = {t['id']: f"{t['name']} ({t['group']})" for t in teams}
    team_ids = list(team_options.keys())
    
    # Organize by Group
    match_groups = sorted(list(set(m.get('group', 'Group 1') for m in matches)))
    
    # Tabs for Groups
    tabs = st.tabs(match_groups)
    
    for idx, group in enumerate(match_groups):
        with tabs[idx]:
            # Filter matches for this group
            group_matches = [m for m in matches if m.get('group', 'Group 1') == group]
            
            # Organize by Round within Group
            rounds = sorted(list(set(m['round'] for m in group_matches)))
            
            for r in rounds:
                with st.expander(f"Round {r}", expanded=True):
                    round_matches = [m for m in group_matches if m['round'] == r]
                    round_matches.sort(key=lambda x: x['match_num'])
                    
                    # Split matches into chunks of 2 for grid layout
                    chunks = [round_matches[i:i+2] for i in range(0, len(round_matches), 2)]
                    
                    for chunk in chunks:
                        cols = st.columns(2)
                        for i, match in enumerate(chunk):
                            with cols[i]:
                                with st.container(border=True): # Card style
                                    st.caption(f"Match {match['match_num']}")
                                    
                                    # Team A
                                    # Filter options: Only show teams in this group? 
                                    # User requirement: "in the match center there are two dropdowns group 1 and group 2".
                                    # Ideally we should only show teams belonging to this group in the dropdowns.
                                    group_teams = [t for t in teams if t.get('group', 'Group 1') == group]
                                    group_team_ids = [t['id'] for t in group_teams]
                                    # Add current selected if not in group (edge case)? No, strict filtering.
                                    
                                    # Fallback if team is not in group (e.g. valid ID but wrong group)? 
                                    # Let's trust the filter or include the currently selected one to be safe.
                                    
                                    current_a = match['team_a_id']
                                    current_b = match['team_b_id']
                                    
                                    # Effective options for this match
                                    match_team_ids = group_team_ids
                                    
                                    ta = st.selectbox("Team A", match_team_ids, 
                                                    index=match_team_ids.index(current_a) if current_a in match_team_ids else None,
                                                    format_func=lambda x: team_options.get(x, "Unknown"),
                                                    key=f"ta_{match['id']}",
                                                    label_visibility="collapsed",
                                                    placeholder="Select Home")
                                    
                                    # Scores Centered
                                    c_s1, c_vs, c_s2 = st.columns([1,1,1])
                                    with c_s1:
                                        sa = st.number_input("Score A", min_value=0, value=match['score_a'], key=f"sa_{match['id']}", label_visibility="collapsed")
                                    with c_vs:
                                        st.markdown("<div style='text-align: center; padding-top: 5px; font-weight: bold;'>VS</div>", unsafe_allow_html=True)
                                    with c_s2:
                                        sb = st.number_input("Score B", min_value=0, value=match['score_b'], key=f"sb_{match['id']}", label_visibility="collapsed")

                                    # Team B
                                    tb = st.selectbox("Team B", match_team_ids,
                                                    index=match_team_ids.index(current_b) if current_b in match_team_ids else None,
                                                    format_func=lambda x: team_options.get(x, "Unknown"),
                                                    key=f"tb_{match['id']}",
                                                    label_visibility="collapsed",
                                                    placeholder="Select Away")

                                    # Update Logic
                                    match['team_a_id'] = ta
                                    match['team_b_id'] = tb
                                    match['score_a'] = sa
                                    match['score_b'] = sb
                                    
                                    if ta and tb and ta != tb:
                                        match['is_complete'] = True
                                        # Use next with default None to avoid crash
                                        t_a_obj = next((t for t in teams if t['id'] == ta), None)
                                        t_b_obj = next((t for t in teams if t['id'] == tb), None)
                                        if t_a_obj: match['team_a_players'] = t_a_obj['players']
                                        if t_b_obj: match['team_b_players'] = t_b_obj['players']
                                    else:
                                        match['is_complete'] = False

    st.divider()
    # Persistence Buttons
    c_save, c_finish = st.columns(2)
    with c_save:
        if st.button("💾 Save Progress", type="primary", use_container_width=True):
            data_manager.save_current_session(session)
            st.toast("Matches Saved Successfully!")
        
    with c_finish:
        if st.button("🏁 Finish Jornada", type="secondary", use_container_width=True):
            history = data_manager.load_matches_history()
            completed = [m for m in matches if m.get('is_complete')]
            history.extend(completed)
            data_manager.save_matches_history(history)
            data_manager.clear_current_session()
            st.success("Jornada Finished! Leaderboard Updated.")
            st.rerun()

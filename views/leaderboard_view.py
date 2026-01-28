import streamlit as st
from utils import data_manager

def render_leaderboard():
    st.header("🏆 Global Leaderboard")
    
    players = data_manager.load_players()
    history = data_manager.load_matches_history()
    
    # Also include current session matches for "Live" updates?
    # User asked for "Auto-update leaderboard from match results"
    # Usually live updates are better.
    session = data_manager.load_current_session()
    current_matches = session['matches'] if session else []
    
    all_matches = history + current_matches
    
    if not players:
        st.info("No players found.")
        return
        
    df = data_manager.calculate_leaderboard(players, all_matches)
    
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Player"),
            "Pts": st.column_config.ProgressColumn("Points", format="%d", min_value=0, max_value=int(df['Pts'].max()) if not df.empty else 0),
            "W": st.column_config.NumberColumn("Wins"),
            "D": st.column_config.NumberColumn("Draws"),
            "L": st.column_config.NumberColumn("Losses"),
            "GD": st.column_config.NumberColumn("Goal Diff"),
        }
    )
    
    with st.expander("Raw Match History"):
        st.json(all_matches)

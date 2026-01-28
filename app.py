import streamlit as st
import utils.data_manager as data_manager
from views import setup_view, match_view, leaderboard_view

# Page Config (Dark Mode / Mobile)
st.set_page_config(
    page_title="3v3 Tracker",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for "Premium" Dark Theme
# Glassmorphism + Neon Accents
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Cards / Containers */
    div[data-testid="stExpander"], div[data-testid="stContainer"] {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Primary Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: none;
        color: white;
        font-weight: bold;
        transition: transform 0.2s;
    }
    button[kind="primary"]:hover {
        transform: scale(1.02);
    }
    
    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b;
        color: white;
        border-radius: 8px;
    }
    
    /* Tables */
    div[data-testid="stDataFrame"] {
        background: #1e293b;
        padding: 1rem;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("⚽ 3v3 Match Tracker")
    
    # Load session state to determine active tab needed?
    # Streamlit Tabs are good.
    
    tab1, tab2, tab3 = st.tabs(["⚡ Match Center", "📊 Leaderboard", "⚙️ Setup"])
    
    with tab1:
        # If no session, prompt to setup
        session = data_manager.load_current_session()
        if session:
            match_view.render_matches()
        else:
            st.warning("No Active Jornada. Go to 'Setup' to start.")
            if st.button("Go to Setup"):
                st.switch_page("app.py") # Only works if multipage, but tabs work differently.
                # Just show message
    
    with tab2:
        leaderboard_view.render_leaderboard()
        
    with tab3:
        setup_view.render_setup()

if __name__ == "__main__":
    main()

import streamlit as st
from services.chat_service import initialize_session
from ui.chat_ui import render_chat_panel
from ui.itinerary_view import render_itinerary_panel

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-header p {
        color: #888;
        font-size: 1rem;
        margin: 0.3rem 0 0 0;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 0.5rem;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        border-color: #667eea;
        color: #667eea;
        transform: translateY(-1px);
    }

    /* Divider */
    hr {
        margin: 0.8rem 0;
        border-color: #f0f0f0;
    }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Initialize session ───────────────────────────────────────
initialize_session()

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
    <h1>✈️ AI Travel Planner</h1>
    <p>Plan your perfect trip with AI — budget, itinerary & more in seconds</p>
</div>
""", unsafe_allow_html=True)

# ── Two column layout ────────────────────────────────────────
left, right = st.columns([1, 1.4], gap="large")

with left:
    render_chat_panel()

with right:
    render_itinerary_panel()
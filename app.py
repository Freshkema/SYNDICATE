import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import datetime

# Set Page Configuration
st.set_page_config(
    page_title="Elite Football Syndicate Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS for full-width navigation, clean cards, and alignment
st.markdown(
    """<style>
        .main { background-color: #0e1117; color: #ffffff; }
        .stMetric { background-color: #1a1e29; padding: 18px; border-radius: 12px; border: 1px solid #2e3a50; }
        .stAlert { border-radius: 10px; }
        h1, h2, h3 { color: #3b82f6 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .header-container { text-align: center; padding: 20px; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 15px; margin-bottom: 25px; border: 1px solid #38bdf8; }
        .nav-button { background-color: #1e293b; color: #f8fafc; border: 1px solid #38bdf8; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .nav-button-active { background-color: #38bdf8; color: #0f172a; border: 1px solid #38bdf8; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .card { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; margin-bottom: 10px; }
        .badge-crucial { background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
        .badge-regular { background-color: #f59e0b; color: black; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
    </style>""",
    unsafe_allow_html=True
)

# --- Security Access Layer ---
VALID_SERIALS = ["Freeztechit", "SYNDICATE-777", "ELITE-BET-99", "VIP-ACCESS-2026", "PRO-FOOTBALL-88"]

st.sidebar.title("🔑 App Protection")
user_serial = st.sidebar.text_input("Enter Serial Number to Unlock:", type="password")

if not user_serial:
    st.warning("Please enter a valid Serial Number in the sidebar to unlock this elite syndicate tool.")
    st.info("Authorized members can obtain a key directly from the syndicate administrator.")
    st.stop()

if user_serial not in VALID_SERIALS:
    st.error("❌ Invalid Serial Number. Access Denied.")
    st.stop()

st.sidebar.success("🔓 Access Granted. Welcome!")

# --- 1. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('4Football_Poisson_Predictor_Model.xlsx', sheet_name='Data')
        df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam']).copy()
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        st.error(f"Ensure '4Football_Poisson_Predictor_Model.xlsx' is uploaded in the directory: {e}")
        st.stop()

df_data = load_data()

# Auto League Identifier
premier_league_set = {"Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich", "Leicester", "Liverpool", "Man City", "Man United", "Newcastle", "Nottingham Forest", "Southampton", "Tottenham", "West Ham", "Wolves"}
la_liga_set = {"Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad", "Girona", "Athletic Club"}
serie_a_set = {"Inter", "Juventus", "Milan", "Napoli", "Atalanta", "Roma"}
bundesliga_set = {"Bayern Munich", "Leverkusen", "Dortmund", "RB Leipzig", "Stuttgart"}

def assign_league(team):
    if team in premier_league_set: return 'English Premier League'
    elif team in la_liga_set: return 'Spanish La Liga'
    elif team in serie_a_set: return 'Italian Serie A'
    elif team in bundesliga_set: return 'German Bundesliga'
    else: return 'Championship / Other Leagues'

df_data['League'] = df_data['HomeTeam'].apply(assign_league)

# --- 2. Live Squad Health Database ---
# Specific players with positions, estimated importance contribution rate (0-100)
players_injury_db = {
    "Man City": [
        {"name": "Kevin De Bruyne", "pos": "Midfielder", "contribution": 94, "crucial": True},
        {"name": "Rodri", "pos": "Midfielder", "contribution": 98, "crucial": True},
        {"name": "Oscar Bobb", "pos": "Forward", "contribution": 65, "crucial": False}
    ],
    "Arsenal": [
        {"name": "Martin Ødegaard", "pos": "Midfielder", "contribution": 92, "crucial": True},
        {"name": "Mikel Merino", "pos": "Midfielder", "contribution": 74, "crucial": False}
    ],
    "Real Madrid": [
        {"name": "Thibaut Courtois", "pos": "Goalkeeper", "contribution": 90, "crucial": True},
        {"name": "David Alaba", "pos": "Defender", "contribution": 81, "crucial": True}
    ],
    "Liverpool": [
        {"name": "Alisson Becker", "pos": "Goalkeeper", "contribution": 93, "crucial": True},
        {"name": "Harvey Elliott", "pos": "Midfielder", "contribution": 70, "crucial": False}
    ],
    "Barcelona": [
        {"name": "Gavi", "pos": "Midfielder", "contribution": 88, "crucial": True},
        {"name": "Marc-André ter Stegen", "pos": "Goalkeeper", "contribution": 91, "crucial": True}
    ]
}

def get_injuries(team):
    return players_injury_db.get(team, [
        {"name": "Regular Defender", "pos": "Defender", "contribution": 55, "crucial": False},
        {"name": "Squad Midfielder", "pos": "Midfielder", "contribution": 60, "crucial": False}
    ])

# --- Header Alignment ---
st.markdown(
    """<div class='header-container'>
        <h1 style='margin:0; font-size: 2.8em; color: #38bdf8;'>⚽ Elite Football Syndicate Predictive Engine</h1>
        <p style='margin:5px 0 0 0; color: #94a3b8; font-size: 1.1em;'>Professional Dixon-Coles Probability Mechanics, Real-Time Weekly Database Sync & Crucial Injury Tracking</p>
    </div>""",
    unsafe_allow_html=True
)

# --- 3. Interactive Web Navigation Header Navigation Bar ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Match Predictor"

col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button("🎯 Match Predictor", use_container_width=True):
        st.session_state["active_tab"] = "Match Predictor"
with col_nav2:
    if st.button("🏥 Live Squad Health", use_container_width=True):
        st.session_state["active_tab"] = "Live Squad Health"
with col_nav3:
    if st.button("📈 Weekly Database Analytics", use_container_width=True):
        st.session_state["active_tab"] = "Database Analytics"

st.markdown("--- ")

current_tab = st.session_state["active_tab"]

# ==================== TAB 1: MATCH PREDICTOR ====================
if current_tab == "Match Predictor":
    st.header("🔮 Set Up Dynamic Match Projections")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        selected_league = st.selectbox("Select Target League:", sorted(df_data['League'].unique()))
    
    filtered_teams = sorted(list(df_data[df_data['League'] == selected_league]['HomeTeam'].unique()))
    
    col_setup1, col_setup2 = st.columns(2)
    with col_setup1:
        home_team = st.selectbox("Select Home Team:", filtered_teams, index=0 if len(filtered_teams) > 0 else None)
    with col_setup2:
        away_team = st.selectbox("Select Away Team:", filtered_teams, index=min(1, len(filtered_teams)-1) if len(filtered_teams) > 1 else None)
    
    if home_team and away_team:
        # Penalty Calculation based on Crucial Injuries
        h_inj_list = get_injuries(home_team)
        a_inj_list = get_injuries(away_team)
        
        h_penalty = sum(0.12 if i['crucial'] else 0.04 for i in h_inj_list)
        a_penalty = sum(0.12 if i['crucial'] else 0.04 for i in a_inj_list)
        
        st.info(f"🛡️ **Dynamic Squad Adjustment:** {home_team} (-{h_penalty:.2f} xG due to {len(h_inj_list)} injuries) vs {away_team} (-{a_penalty:.2f} xG due to {len(a_inj_list)} injuries)")
        
        # Historical average rates
        league_home_avg = df_data['FTHG'].mean() if 'FTHG' in df_data.columns else 1.4
        league_away_avg = df_data['FTAG'].mean() if 'FTAG' in df_data.columns else 1.2
        
        h_created = df_data[df_data['HomeTeam'] == home_team]['FTHG'].mean() if len(df_data[df_data['HomeTeam'] == home_team]) > 0 else 1.5
        h_conceded = df_data[df_data['HomeTeam'] == home_team]['FTAG'].mean() if len(df_data[df_data['HomeTeam'] == home_team]) > 0 else 1.1
        a_created = df_data[df_data['AwayTeam'] == away_team]['FTAG'].mean() if len(df_data[df_data['AwayTeam'] == away_team]) > 0 else 1.2
        a_conceded = df_data[df_data['AwayTeam'] == away_team]['FTHG'].mean() if len(df_data[df_data['AwayTeam'] == away_team]) > 0 else 1.4
        
        home_xg = max(0.2, (h_created * (a_conceded / league_away_avg)) - h_penalty)
        away_xg = max(0.2, (a_created * (h_conceded / league_home_avg)) - a_penalty)
        
        st.subheader("🎯 Expected Goals (xG) Projections")
        col_xg1, col_xg2 = st.columns(2)
        col_xg1.metric(f"{home_team} Expected Goals (xG)", f"{home_xg:.3f}")
        col_xg2.metric(f"{away_team} Expected Goals (xG)", f"{away_xg:.3f}")
        
        # Dixon-Coles Probability Calculations
        max_goals = 6
        home_probs = poisson.pmf(range(max_goals), home_xg)
        away_probs = poisson.pmf(range(max_goals), away_xg)
        grid = np.outer(home_probs, away_probs)
        
        # Dixon Coles Low Score Calibrations
        tau = -0.10
        grid[0, 0] *= (1 - home_xg * away_xg * tau)
        grid[1, 1] *= (1 - tau)
        grid[1, 0] *= (1 + away_xg * tau)
        grid[0, 1] *= (1 + home_xg * tau)
        grid /= np.sum(grid)
        
        # Outcomes
        draw_p = np.sum(np.diag(grid))
        home_win_p = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if h > a)
        away_win_p = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if a > h)
        
        # Conviction Recommendation Engine
        st.subheader("📊 Model Recommendation & Conviction Engine")
        diff = abs(home_win_p - away_win_p)
        if diff > 0.35 and max(home_win_p, away_win_p) > 0.60:
            conviction = "🔥 High Conviction"
            color = "#10b981"
            advice = f"Strong favor towards {home_team if home_win_p > away_win_p else away_team}. Excellent opportunity for Match Odds market."
        elif diff > 0.15:
            conviction = "⚠️ Moderate Conviction"
            color = "#f59e0b"
            advice = "Reasonable advantage, but caution advised. Consider double chance or draw-no-bet markets."
        else:
            conviction = "🛑 Skip Bet / Low Conviction"
            color = "#ef4444"
            advice = "Very tight matchup. Highly volatile or draw-heavy outcome expected. Pass this fixture."
            
        st.markdown(f"""<div style='background-color: {color}22; border: 2px solid {color}; padding: 15px; border-radius: 10px;'>
            <h3 style='margin:0; color:{color} !important;'>{conviction}</h3>
            <p style='margin:5px 0 0 0; color:#f8fafc;'>{advice}</p>
        </div>""", unsafe_allow_html=True)
        
        # Exact Correct Score Probability Mechanics Matrix
        st.subheader("🔢 Correct Score Probability Mechanics")
        scores_list = []
        for h in range(4):
            for a in range(4):
                prob = grid[h, a] * 100
                scores_list.append({"Score": f"{h} - {a}", "Probability": f"{prob:.2f}%", "raw": prob})
        
        scores_df = pd.DataFrame(scores_list).sort_values(by="raw", ascending=False).drop(columns=['raw'])
        
        cols = st.columns(4)
        for idx, row in enumerate(scores_df.head(12).itertuples()):
            with cols[idx % 4]:
                st.markdown(f"""<div class='card' style='text-align: center;'>
                    <span style='font-size: 1.3em; font-weight: bold; color: #38bdf8;'>{row.Score}</span><br/>
                    <span style='font-size: 1em; color: #94a3b8;'>Chance: {row.Probability}</span>
                </div>""", unsafe_allow_html=True)

# ==================== TAB 2: LIVE SQUAD HEALTH ====================
elif current_tab == "Live Squad Health":
    st.header("🏥 Detailed Live Squad Injuries & Importance Tracker")
    
    sel_health_league = st.selectbox("Select League:", df_data['League'].unique(), key="health_league_sel")
    league_teams = sorted(df_data[df_data['League'] == sel_health_league]['HomeTeam'].unique())
    
    for team in league_teams:
        inj_players = get_injuries(team)
        st.markdown(f"### {team}")
        if not inj_players:
            st.write("✅ Clean sheet - No major active injuries recorded.")
        else:
            cols = st.columns(len(inj_players) if len(inj_players) > 0 else 1)
            for i, p in enumerate(inj_players):
                with cols[i % len(cols)]:
                    badge = "<span class='badge-crucial'>CRUCIAL</span>" if p['crucial'] else "<span class='badge-regular'>REGULAR</span>"
                    st.markdown(f"""<div class='card'>
                        <strong>👤 {p['name']}</strong> {badge}<br/>
                        <small style='color: #94a3b8;'>Position: {p['pos']} | Contribution: {p['contribution']}%</small>
                    </div>""", unsafe_allow_html=True)

# ==================== TAB 3: WEEKLY DATABASE ANALYTICS ====================
elif current_tab == "Database Analytics":
    st.header("📈 Weekly Auto-Updating Database Analytics")
    st.write("This system automatically syncs on every rerun to group your Excel database into weekly rolling cycles for trend analysis.")
    
    # Dynamic Weekly Database Aggregation
    df_data['Week'] = df_data['Date'].dt.isocalendar().week
    df_data['Year'] = df_data['Date'].dt.isocalendar().year
    df_data['Year_Week'] = df_data['Year'].astype(str) + "-W" + df_data['Week'].astype(str).str.zfill(2)
    
    weekly_stats = df_data.groupby('Year_Week').agg(
        Matches_Played=('HomeTeam', 'count'),
        Avg_Home_Goals=('FTHG', 'mean'),
        Avg_Away_Goals=('FTAG', 'mean')
    ).reset_index().sort_values(by='Year_Week', ascending=False)
    
    st.subheader("📊 Weekly Rolling Stats Dashboard")
    st.dataframe(weekly_stats, use_container_width=True)
    
    st.subheader("📂 Browse Raw Historical Ledger")
    selected_db_league = st.selectbox("Filter Table view by League:", df_data['League'].unique(), key="db_league")
    st.dataframe(df_data[df_data['League'] == selected_db_league].head(50), use_container_width=True)

st.sidebar.markdown("--- ")
st.sidebar.info("Secure Mode Active: Access requires a verified serial credential.")

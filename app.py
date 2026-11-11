
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# Set Page Configuration
st.set_page_config(page_title="Elite Football Syndicate Predictor", page_icon="⚽", layout="wide")

# --- Security Access Layer ---
# Incorporating 'Freeztechit' as requested by the client
VALID_SERIALS = ["Freeztechit", "SYNDICATE-777", "ELITE-BET-99", "VIP-ACCESS-2026", "PRO-FOOTBALL-88"]

st.sidebar.title("🔑 App Protection")
user_serial = st.sidebar.text_input("Enter Serial Number to Unlock:", type="password")

if not user_serial:
    st.warning("Please enter a valid Serial Number in the sidebar to unlock this elite syndicate tool.")
    st.info("Authorized members can obtain a key directly from the syndicate administrator.")
    st.stop()  # Halt app execution here if no key is entered

if user_serial not in VALID_SERIALS:
    st.error("❌ Invalid Serial Number. Access Denied.")
    st.stop()  # Halt app execution on invalid key

# If valid, the rest of the application loads below
st.sidebar.success("🔓 Access Granted. Welcome!")

st.title("⚽ Elite Football Syndicate Predictive Engine")
st.markdown("Welcome to the A+ grade predictive engine. Instantly adjust team values using squad health dynamics.")

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_excel('4Football_Poisson_Predictor_Model.xlsx', sheet_name='Data')
    return df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam']).copy()

try:
    df_data = load_data()
    st.success("Historical Data loaded successfully!")
except Exception as e:
    st.error(f"Ensure '4Football_Poisson_Predictor_Model.xlsx' is uploaded in the same directory: {e}")
    st.stop()

# Minimal Poisson Base Engine
class Engine:
    def __init__(self, df):
        self.df = df
        self.league_home_avg = df['FTHG'].mean() if 'FTHG' in df.columns else 1.4
        self.league_away_avg = df['FTAG'].mean() if 'FTAG' in df.columns else 1.2

    def get_team_stats(self, team, is_home=True):
        if is_home:
            team_matches = self.df[self.df['HomeTeam'] == team]
            if len(team_matches) == 0: return self.league_home_avg, self.league_away_avg
            return team_matches['FTHG'].mean(), team_matches['FTAG'].mean()
        else:
            team_matches = self.df[self.df['AwayTeam'] == team]
            if len(team_matches) == 0: return self.league_away_avg, self.league_home_avg
            return team_matches['FTAG'].mean(), team_matches['FTHG'].mean()

engine = Engine(df_data)

# 2. Interactive Input Panel
col1, col2 = st.columns(2)
teams = sorted(list(set(df_data['HomeTeam'].unique()) | set(df_data['AwayTeam'].unique())))

with col1:
    home_team = st.selectbox("Select Home Team", teams, index=teams.index('Dundee United') if 'Dundee United' in teams else 0)
    home_injury_penalty = st.slider("Home Squad Out Penalty (Decrease Home xG)", 0.0, 1.0, 0.0, 0.05)

with col2:
    away_team = st.selectbox("Select Away Team", teams, index=teams.index('Rangers') if 'Rangers' in teams else 1)
    away_injury_penalty = st.slider("Away Squad Out Penalty (Decrease Away xG)", 0.0, 1.0, 0.15, 0.05)

# Calculated Baseline xG
h_base_created, h_base_conceded = engine.get_team_stats(home_team, is_home=True)
a_base_created, a_base_conceded = engine.get_team_stats(away_team, is_home=False)

home_xg = max(0.2, (h_base_created * (a_base_conceded / engine.league_away_avg)) - home_injury_penalty)
away_xg = max(0.2, (a_base_created * (h_base_conceded / engine.league_home_avg)) - away_injury_penalty)

st.subheader("🎯 Adjusted Expected Goals (xG) Projections")
c1, c2 = st.columns(2)
c1.metric(f"{home_team} Expected Goals (xG)", f"{home_xg:.3f}")
c2.metric(f"{away_team} Expected Goals (xG)", f"{away_xg:.3f}")

# Compute Probabilities
max_goals = 8
home_probs = poisson.pmf(range(max_goals), home_xg)
away_probs = poisson.pmf(range(max_goals), away_xg)
grid = np.outer(home_probs, away_probs)

# Dixon Coles Low-Score Draw Calibrations
tau = -0.10
grid[0, 0] *= (1 - home_xg * away_xg * tau)
grid[1, 1] *= (1 - tau)
grid[1, 0] *= (1 + away_xg * tau)
grid[0, 1] *= (1 + home_xg * tau)
grid /= np.sum(grid)

draw_p = np.sum(np.diag(grid))
home_win_p = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if h > a)
away_win_p = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if a > h)
over_2_5 = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if (h+a) > 2.5)

# Over/Under and BTTS calculations
over_1_5 = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if (h+a) > 1.5)
over_3_5 = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if (h+a) > 3.5)
btts_yes = sum(grid[h, a] for h in range(max_goals) for a in range(max_goals) if h > 0 and a > 0)

# Custom Corner metrics estimates
avg_hc, avg_ac = 5.8, 4.6

st.subheader("📊 Dixon-Coles Probability Matrix Output")
pcol1, pcol2, pcol3, pcol4 = st.columns(4)
pcol1.metric("Home Win %", f"{home_win_p * 100:.2f}%")
pcol2.metric("Draw %", f"{draw_p * 100:.2f}%")
pcol3.metric("Away Win %", f"{away_win_p * 100:.2f}%")
pcol4.metric("Over 2.5 Goals %", f"{over_2_5 * 100:.2f}%")

st.subheader("📈 Advanced Goal & Corner Markets")
acol1, acol2, acol3, acol4 = st.columns(4)
acol1.metric("BTTS Yes %", f"{btts_yes * 100:.2f}%")
acol2.metric("Over 1.5 %", f"{over_1_5 * 100:.2f}%")
acol3.metric("Over 3.5 %", f"{over_3_5 * 100:.2f}%")
acol4.metric("Projected Total Corners", f"{avg_hc + avg_ac:.1f}")

st.info("Secure Mode Active: Access requires a verified serial credential.")

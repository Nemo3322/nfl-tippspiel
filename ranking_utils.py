import streamlit as st
import pandas as pd
from config import USERS, POINTS_CONFIG, AFC_DIVISIONS, NFC_DIVISIONS, HALL_OF_FAME
from db_utils import load_data

def calculate_user_points(username):
    user_data = load_data(f"tipp_{username}")
    official_data = load_data("official_results")

    if not user_data or not official_data:
        return 0, {}

    score_details = {
        "division_pts": 0,
        "qualifier_pts": 0,
        "seed_pts": 0,
        "exit_pts": 0,
        "sb_pts": 0
    }

    # 1. Division-Platzierungen (2 Pkt)
    all_divs = list(AFC_DIVISIONS.keys()) + list(NFC_DIVISIONS.keys())
    for div_key in all_divs:
        u_div = user_data.get(div_key, [])
        o_div = official_data.get(div_key, [])
        if isinstance(u_div, list) and isinstance(o_div, list):
            for pos in range(min(len(u_div), len(o_div))):
                if u_div[pos] != "-- Bitte wählen --" and u_div[pos] == o_div[pos]:
                    score_details["division_pts"] += POINTS_CONFIG["EXACT_DIVISION_POS"]

    # 2. Playoff-Teilnehmer (5 Pkt) & Exakte Seeds (10 Pkt)
    for conf in ["afc", "nfc"]:
        u_seeds = user_data.get(f"{conf}_seeds") or user_data.get(f"{conf.upper()}_seeds") or {}
        o_seeds = official_data.get(f"{conf}_seeds") or official_data.get(f"{conf.upper()}_seeds") or {}

        if isinstance(u_seeds, dict) and isinstance(o_seeds, dict):
            u_teams = {str(k): v for k, v in u_seeds.items()}
            o_teams = {str(k): v for k, v in o_seeds.items()}
            o_teams_set = set(o_teams.values())

            for pos_key, u_team in u_teams.items():
                if u_team != "-- Bitte wählen --":
                    if u_team in o_teams_set:
                        score_details["qualifier_pts"] += POINTS_CONFIG["PLAYOFF_QUALIFIER"]
                    if o_teams.get(pos_key) == u_team:
                        score_details["seed_pts"] += POINTS_CONFIG["EXACT_SEED_POS"]

    # 3. Exakter Playoff-Ausstieg (15 Pkt)
    u_exits = user_data.get("playoff_exits", {})
    o_exits = official_data.get("playoff_exits", {})
    if isinstance(u_exits, dict) and isinstance(o_exits, dict):
        for team, user_exit_round in u_exits.items():
            if team != "-- Bitte wählen --" and team in o_exits:
                if o_exits[team] == user_exit_round:
                    score_details["exit_pts"] += POINTS_CONFIG["EXACT_PLAYOFF_EXIT"]

    # 4. Super Bowl Sieger (25 Pkt)
    u_sb = user_data.get("super_bowl_winner")
    o_sb = official_data.get("super_bowl_winner")
    if u_sb and o_sb and u_sb != "-- Bitte wählen --" and u_sb == o_sb:
        score_details["sb_pts"] += POINTS_CONFIG["SUPER_BOWL_WINNER"]

    total_score = sum(score_details.values())
    return total_score, score_details


def render_leaderboard_page():
    st.header("🏆 Rangliste & Hall of Fame")

    tab1, tab2 = st.tabs(["📊 Aktuelle Saison", "🏛️ Hall of Fame (Historie)"])

    with tab1:
        official_data = load_data("official_results")
        if not official_data:
            st.info("ℹ️ Die Saison-Ergebnisse wurden noch nicht vom Admin eingetragen. Sobald der Admin die ersten Ergebnisse speichert, erscheint hier die Punkteübersicht!")
        else:
            leaderboard_data = []
            for username in USERS.keys():
                total_score, details = calculate_user_points(username)
                leaderboard_data.append({
                    "Spieler": username.capitalize(),
                    "Gesamtpunkte": total_score,
                    "Divisions (2P)": details.get("division_pts", 0),
                    "Playoff-Teams (5P)": details.get("qualifier_pts", 0),
                    "Exakte Seeds (10P)": details.get("seed_pts", 0),
                    "Ausstiegs-Runde (15P)": details.get("exit_pts", 0),
                    "Super Bowl Sieger (25P)": details.get("sb_pts", 0)
                })

            df = pd.DataFrame(leaderboard_data)
            df = df.sort_values(by="Gesamtpunkte", ascending=False).reset_index(drop=True)

            ranks = []
            for i in range(len(df)):
                if i == 0: ranks.append("🥇 1. Platz")
                elif i == 1: ranks.append("🥈 2. Platz")
                elif i == 2: ranks.append("🥉 3. Platz")
                else: ranks.append(f"{i+1}. Platz")
            df["Rang"] = ranks

            cols_order = ["Rang", "Spieler", "Gesamtpunkte", "Divisions (2P)", "Playoff-Teams (5P)", "Exakte Seeds (10P)", "Ausstiegs-Runde (15P)", "Super Bowl Sieger (25P)"]
            df = df[cols_order]

            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("🏛️ Die bisherigen Champions")
        st.write("Ewige Siegerliste der vergangenen Tippspiel-Jahre:")
        df_hof = pd.DataFrame(HALL_OF_FAME)
        st.dataframe(df_hof, use_container_width=True, hide_index=True)


def render_points_system_page():
    st.header("📖 Punktesystem Übersicht")
    st.write("So werden eure Punkte nach der Saison berechnet:")

    st.markdown("""
    | Kategorie | Beschreibung | Punkte |
    | :--- | :--- | :---: |
    | **Richtige Divisions-Platzierung** | Für jedes Team, das exakt auf dem richtigen Platz in seiner Division gelandet ist (1–4) | **2 Punkte** |
    | **Playoff-Teilnehmer** | Für jedes Team, das es tatsächlich in die Playoffs geschafft hat (Seed 1–7) | **5 Punkte** |
    | **Exakter Playoff-Seed** | Für jedes Team, das exakt auf dem von dir getippten Seed-Platz gelandet ist (1–7) | **10 Punkte** |
    | **Exakte Playoff-Etappe** | Für jedes Team, das genau in der von dir getippten Runde (Wild Card, Divisional etc.) ausscheidet | **15 Punkte** |
    | **Super Bowl Champion** | Für den exakt richtigen Tipp des Super Bowl Champions | **25 Punkte** |
    """)

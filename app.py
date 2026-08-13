import streamlit as st
import json
import os
from config import USERS, EMPTY_OPTION, AFC_DIVISIONS, NFC_DIVISIONS, TEAM_LOGOS, CONF_LOGOS, LOCK_DEADLINE, is_locked
from playoff_utils import render_playoff_page
from ranking_utils import render_leaderboard_page, render_points_system_page
from admin_utils import render_admin_page
from home_utils import render_home_page

# Seitenkonfiguration
st.set_page_config(page_title="NFL Prediction", page_icon="🏈")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def render_division_tipps(conference_name, divisions_dict, user_file):
    col_h1, col_h2 = st.columns([1, 10])
    with col_h1:
        st.image(CONF_LOGOS.get(conference_name), width=55)
    with col_h2:
        st.header(f"{conference_name} Divisions tippen")

    locked = is_locked()
    if locked:
        st.error(f"🔒 Die Tippabgabe ist seit dem {LOCK_DEADLINE.strftime('%d.%m.%Y um %H:%M Uhr')} geschlossen!")
    else:
        st.write("Wähle für jede Division die Teams für die fixen Platzierungen 1–4.")

    saved_data = {}
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            try:
                saved_data = json.load(f)
            except Exception:
                saved_data = {}

    for div_key, teams in divisions_dict.items():
        st.subheader(div_key.replace("_", " ").upper())

        for pos in range(1, 5):
            state_key = f"{div_key}_pos_{pos}"
            if state_key not in st.session_state:
                if div_key in saved_data and isinstance(saved_data[div_key], list) and len(saved_data[div_key]) >= pos:
                    saved_val = saved_data[div_key][pos - 1]
                    st.session_state[state_key] = saved_val if saved_val in teams else EMPTY_OPTION
                else:
                    st.session_state[state_key] = EMPTY_OPTION

        cols = st.columns(4)
        for i in range(1, 5):
            state_key = f"{div_key}_pos_{i}"
            current_val = st.session_state[state_key]

            chosen_other = [
                st.session_state.get(f"{div_key}_pos_{j}") 
                for j in range(1, 5) if j != i and st.session_state.get(f"{div_key}_pos_{j}") != EMPTY_OPTION
            ]

            options = [EMPTY_OPTION] + [t for t in teams if t not in chosen_other]
            idx = options.index(current_val) if current_val in options else 0

            with cols[i - 1]:
                st.selectbox(f"Platz {i}", options=options, index=idx, key=state_key, disabled=locked)

        selection = [st.session_state.get(f"{div_key}_pos_{p}") for p in range(1, 5)]
        if all(s != EMPTY_OPTION for s in selection) and len(set(selection)) == 4:
            medals = ["🥇", "🥈", "🥉", "4️⃣"]
            cols_medal = st.columns(4)
            for idx_m, team in enumerate(selection):
                with cols_medal[idx_m]:
                    url = TEAM_LOGOS.get(team)
                    if url:
                        st.image(url, width=80)
                    st.markdown(f"{medals[idx_m]} **{team}**")

    st.markdown("---")
    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if st.button(f"{conference_name}-Tipps speichern 💾", use_container_width=True, disabled=locked):
            all_valid = True
            for div_key in divisions_dict.keys():
                ordered = [st.session_state.get(f"{div_key}_pos_{p}") for p in range(1, 5)]
                if EMPTY_OPTION in ordered:
                    st.error(f"Bitte wähle alle 4 Plätze für {div_key.replace('_', ' ').upper()} aus.")
                    all_valid = False
                    break

            if all_valid:
                for div_key in divisions_dict.keys():
                    saved_data[div_key] = [st.session_state.get(f"{div_key}_pos_{p}") for p in range(1, 5)]

                with open(user_file, "w") as f:
                    json.dump(saved_data, f)
                st.success(f"Deine {conference_name}-Tipps wurden erfolgreich gespeichert!")

    with btn_col2:
        if st.button(f"{conference_name}-Tipps zurücksetzen 🗑️", type="secondary", use_container_width=True, disabled=locked):
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    try:
                        file_data = json.load(f)
                    except Exception:
                        file_data = {}
                
                for div_key in divisions_dict.keys():
                    file_data.pop(div_key, None)

                with open(user_file, "w") as f:
                    json.dump(file_data, f)

            for div_key in divisions_dict.keys():
                for pos in range(1, 5):
                    key = f"{div_key}_pos_{pos}"
                    if key in st.session_state:
                        del st.session_state[key]
            st.rerun()

# --- HAUPT-APP ---
if not st.session_state["logged_in"]:
    st.title("🏈 NFL Tippspiel")
    st.subheader("Bitte anmelden")
    
    username_input = st.text_input("Benutzername").lower()
    password_input = st.text_input("Passwort", type="password")
    
    if st.button("Einloggen"):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username_input
            st.success(f"Willkommen zurück, {username_input.capitalize()}!")
            st.rerun()
        else:
            st.error("Falscher Benutzername oder Passwort.")

else:
    st.sidebar.write(f"Eingeloggt als: **{st.session_state['username'].capitalize()}**")
    if st.sidebar.button("Ausloggen"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    
    # Menüoptionen (Admin-Menü nur für den User 'mirco')
    nav_options = ["Home", "AFC Tipps", "NFC Tipps", "Playoffs", "Rangliste", "Punktesystem"]
    if st.session_state["username"] == "mirco":
        nav_options.append("⚙️ Admin (Ergebnisse)")

    page = st.sidebar.radio("Navigation", nav_options)
    user_file = f"tipp_{st.session_state['username']}.json"

    if page == "Home":
        render_home_page()

    elif page == "AFC Tipps":
        render_division_tipps("AFC", AFC_DIVISIONS, user_file)

    elif page == "NFC Tipps":
        render_division_tipps("NFC", NFC_DIVISIONS, user_file)

    elif page == "Playoffs":
        render_playoff_page(user_file)

    elif page == "Rangliste":
        render_leaderboard_page()

    elif page == "Punktesystem":
        render_points_system_page()

    elif page == "⚙️ Admin (Ergebnisse)":
        render_admin_page()

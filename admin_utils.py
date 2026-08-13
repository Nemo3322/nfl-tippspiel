import streamlit as st
import json
import os
from config import EMPTY_OPTION, AFC_DIVISIONS, NFC_DIVISIONS, OFFICIAL_RESULTS_FILE

def render_admin_page():
    st.header("⚙️ Admin-Bereich: Offizielle Saison-Ergebnisse eintragen")
    st.write("Trage hier die echten Endergebnisse der Saison ein, um die Rangliste zu berechnen.")

    saved_results = {}
    if os.path.exists(OFFICIAL_RESULTS_FILE):
        with open(OFFICIAL_RESULTS_FILE, "r") as f:
            try:
                saved_results = json.load(f)
            except Exception:
                saved_results = {}

    # 1. DIVISIONS
    st.subheader("1. Echte Divisions-Endergebnisse")
    all_divisions = {**AFC_DIVISIONS, **NFC_DIVISIONS}

    for div_key, teams in all_divisions.items():
        st.markdown(f"**{div_key.replace('_', ' ').upper()}**")
        cols = st.columns(4)
        for pos in range(1, 5):
            key = f"admin_{div_key}_pos_{pos}"
            saved_val = saved_results.get(div_key, [EMPTY_OPTION]*4)[pos-1] if div_key in saved_results else EMPTY_OPTION
            idx = teams.index(saved_val) + 1 if saved_val in teams else 0

            with cols[pos - 1]:
                st.selectbox(f"Platz {pos}", options=[EMPTY_OPTION] + teams, index=idx, key=key)

    st.markdown("---")

    # 2. SEEDS (1-7)
    st.subheader("2. Echte Playoff Seeds (1–7)")
    col_a, col_n = st.columns(2)

    afc_playoff_teams = []
    nfc_playoff_teams = []

    for conf, col, target_list in [("afc", col_a, afc_playoff_teams), ("nfc", col_n, nfc_playoff_teams)]:
        with col:
            st.markdown(f"**{conf.upper()} Seeds**")
            all_conf_teams = []
            divs = AFC_DIVISIONS if conf == "afc" else NFC_DIVISIONS
            for t_list in divs.values(): 
                all_conf_teams.extend(t_list)

            for seed_pos in range(1, 8):
                key = f"admin_{conf}_seed_{seed_pos}"
                saved_seed = saved_results.get(f"{conf}_seeds", {}).get(str(seed_pos), EMPTY_OPTION)
                idx = all_conf_teams.index(saved_seed) + 1 if saved_seed in all_conf_teams else 0

                selected_team = st.selectbox(f"Seed #{seed_pos}", options=[EMPTY_OPTION] + all_conf_teams, index=idx, key=key)
                if selected_team != EMPTY_OPTION:
                    target_list.append(selected_team)

    st.markdown("---")

    # 3. AUSSTIEGS-RUNDEN
    st.subheader("3. Echte Playoff-Ausstiegsrunden (15 Pkt Kategorie)")
    
    if not afc_playoff_teams and not nfc_playoff_teams:
        st.info("ℹ️ Bitte wähle zuerst oben bei den Playoff-Seeds (Schritt 2) die Teams aus.")
    else:
        st.write("Wähle für die gewählten Playoff-Teams aus, in welcher Runde sie TATSÄCHLICH ausgeschieden sind:")
        
        rounds_options = [EMPTY_OPTION, "Wild Card", "Divisional Round", "Conference Championship", "Super Bowl Runner-Up"]
        saved_exits = saved_results.get("playoff_exits", {})
        admin_exits = {}

        col_exit_a, col_exit_n = st.columns(2)

        # AFC Verlierer
        with col_exit_a:
            st.markdown("**AFC Playoff-Teams**")
            for team in afc_playoff_teams:
                curr_exit = saved_exits.get(team, EMPTY_OPTION)
                idx_r = rounds_options.index(curr_exit) if curr_exit in rounds_options else 0
                admin_exits[team] = st.selectbox(f"Aus für **{team}** in:", options=rounds_options, index=idx_r, key=f"admin_exit_{team}")

        # NFC Verlierer
        with col_exit_n:
            st.markdown("**NFC Playoff-Teams**")
            for team in nfc_playoff_teams:
                curr_exit = saved_exits.get(team, EMPTY_OPTION)
                idx_r = rounds_options.index(curr_exit) if curr_exit in rounds_options else 0
                admin_exits[team] = st.selectbox(f"Aus für **{team}** in:", options=rounds_options, index=idx_r, key=f"admin_exit_{team}")

    st.markdown("---")

    # 4. SUPER BOWL CHAMPION
    st.subheader("4. Echter Super Bowl Champion")
    all_playoff_teams = afc_playoff_teams + nfc_playoff_teams
    saved_sb = saved_results.get("super_bowl_winner", EMPTY_OPTION)
    sb_options = [EMPTY_OPTION] + all_playoff_teams
    sb_idx = sb_options.index(saved_sb) if saved_sb in sb_options else 0

    actual_sb_winner = st.selectbox("Super Bowl Sieger 2026:", options=sb_options, index=sb_idx, key="admin_sb_winner")

    st.markdown("---")
    
    # AKTION-BUTTONS: SPEICHERN & ZURÜCKSETZEN
    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if st.button("Offizielle Ergebnisse speichern 💾", type="primary", use_container_width=True):
            results_to_save = {}

            # Divisions speichern
            for div_key in all_divisions.keys():
                results_to_save[div_key] = [st.session_state.get(f"admin_{div_key}_pos_{p}") for p in range(1, 5)]

            # Seeds speichern
            for conf in ["afc", "nfc"]:
                results_to_save[f"{conf}_seeds"] = {str(p): st.session_state.get(f"admin_{conf}_seed_{p}") for p in range(1, 8)}

            # Playoff Exits speichern
            if all_playoff_teams:
                results_to_save["playoff_exits"] = {team: r for team, r in admin_exits.items() if r != EMPTY_OPTION}

            # Super Bowl Sieger
            results_to_save["super_bowl_winner"] = actual_sb_winner

            with open(OFFICIAL_RESULTS_FILE, "w") as f:
                json.dump(results_to_save, f)

            st.success("✅ Offizielle Ergebnisse wurden erfolgreich gespeichert! Die Rangliste ist nun aktualisiert.")

    with btn_col2:
        if st.button("Offizielle Ergebnisse zurücksetzen 🗑️", type="secondary", use_container_width=True):
            if os.path.exists(OFFICIAL_RESULTS_FILE):
                os.remove(OFFICIAL_RESULTS_FILE)

            for key in list(st.session_state.keys()):
                if key.startswith("admin_"):
                    del st.session_state[key]

            st.rerun()

    # DATEI-INSPECTOR (Gespeicherte .json Dateien ansehen & herunterladen)
    st.markdown("---")
    st.subheader("📁 Gespeicherte Tipp-Dateien ansehen & herunterladen")
    
    json_files = [f for f in os.listdir(".") if f.endswith(".json")]
    if json_files:
        selected_file = st.selectbox("Wähle eine Datei zum Ansehen/Herunterladen:", options=json_files)
        if selected_file:
            with open(selected_file, "r") as f:
                try:
                    file_content = f.read()
                    data = json.loads(file_content)
                    
                    # Button zum Herunterladen der JSON-Datei
                    st.download_button(
                        label=f"📥 {selected_file} herunterladen",
                        data=file_content,
                        file_name=selected_file,
                        mime="application/json"
                    )
                    
                    # Vorschau im Browser
                    st.json(data)
                except Exception:
                    st.error("Datei konnte nicht gelesen werden.")
                    data = json.load(f)
                    st.json(data)
                except Exception:
                    st.error("Datei konnte nicht gelesen werden.")

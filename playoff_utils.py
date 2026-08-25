import streamlit as st
from config import EMPTY_OPTION, AFC_DIVISIONS, NFC_DIVISIONS, TEAM_LOGOS, CONF_LOGOS, LOCK_DEADLINE, is_locked
from db_utils import load_data, save_data

def render_seed_selection(conf_name, divisions_dict, saved_data):
    col_title1, col_title2 = st.columns([1, 5])
    with col_title1:
        st.image(CONF_LOGOS.get(conf_name), width=50)
    with col_title2:
        st.subheader(f"{conf_name} Playoff Seeding")

    div_winners = [saved_data[div][0] for div in divisions_dict.keys() if isinstance(saved_data.get(div), list)]
    other_teams = []
    for div in divisions_dict.keys():
        if isinstance(saved_data.get(div), list):
            other_teams.extend(saved_data[div][1:])

    seeds = {}
    col_seeds1, col_seeds2 = st.columns(2)
    saved_seeds = saved_data.get(f"{conf_name.lower()}_seeds", {})

    with col_seeds1:
        st.markdown("**Division Winners (Seeds 1–4)**")
        for pos in range(1, 5):
            key = f"{conf_name}_seed_{pos}"
            chosen = [st.session_state.get(f"{conf_name}_seed_{j}") for j in range(1, 5) if j != pos]
            opts = [EMPTY_OPTION] + [t for t in div_winners if t not in chosen]
            
            # Initialisieren aus Datenbank, falls noch nicht im Session State
            if key not in st.session_state:
                saved_val = saved_seeds.get(str(pos), EMPTY_OPTION)
                st.session_state[key] = saved_val if saved_val in opts else EMPTY_OPTION

            curr = st.session_state.get(key)
            if curr not in opts:
                curr = EMPTY_OPTION
                st.session_state[key] = EMPTY_OPTION

            idx = opts.index(curr)
            seeds[pos] = st.selectbox(f"Seed #{pos}", options=opts, index=idx, key=key, disabled=is_locked())

    with col_seeds2:
        st.markdown("**Wild Cards (Seeds 5–7)**")
        for pos in range(5, 8):
            key = f"{conf_name}_seed_{pos}"
            chosen = [st.session_state.get(f"{conf_name}_seed_{j}") for j in range(5, 8) if j != pos]
            opts = [EMPTY_OPTION] + [t for t in other_teams if t not in chosen]
            
            # Initialisieren aus Datenbank, falls noch nicht im Session State
            if key not in st.session_state:
                saved_val = saved_seeds.get(str(pos), EMPTY_OPTION)
                st.session_state[key] = saved_val if saved_val in opts else EMPTY_OPTION

            curr = st.session_state.get(key)
            if curr not in opts:
                curr = EMPTY_OPTION
                st.session_state[key] = EMPTY_OPTION

            idx = opts.index(curr)
            seeds[pos] = st.selectbox(f"Seed #{pos}", options=opts, index=idx, key=key, disabled=is_locked())

    return seeds


def safe_radio(label, options, key_name, saved_bracket_picks):
    # Gespeicherten Sieger wiederherstellen, falls Key noch nicht in session_state existiert
    if key_name not in st.session_state:
        saved_val = saved_bracket_picks.get(key_name)
        if saved_val in options:
            st.session_state[key_name] = saved_val

    curr_val = st.session_state.get(key_name)
    idx_val = options.index(curr_val) if curr_val in options else 0
    return st.radio(label, options=options, index=idx_val, key=key_name, disabled=is_locked())


def render_playoff_page(username):
    st.header("🏈 NFL Playoff Bracket")

    if is_locked():
        st.error(f"🔒 Das Playoff-Bracket ist seit dem {LOCK_DEADLINE.strftime('%d.%m.%Y um %H:%M Uhr')} gesperrt!")

    user_key = f"tipp_{username}"
    saved_data = load_data(user_key)
    saved_bracket_picks = saved_data.get("bracket_picks", {})

    all_afc_done = all(k in saved_data and isinstance(saved_data[k], list) and len(saved_data[k]) == 4 for k in AFC_DIVISIONS.keys())
    all_nfc_done = all(k in saved_data and isinstance(saved_data[k], list) and len(saved_data[k]) == 4 for k in NFC_DIVISIONS.keys())

    if not (all_afc_done and all_nfc_done):
        st.warning("⚠️ Bitte tippe zuerst ALLE AFC und NFC Divisionen vollständig und speichere sie ab, bevor du die Playoffs tippst!")
        return

    st.info("Ordne zuerst die Playoff-Seeds (1-7) an. Daraus ergibt sich automatisch dein Bracket!")

    st.markdown("---")
    col_afc_s, col_nfc_s = st.columns(2)
    
    with col_afc_s:
        afc_seeds = render_seed_selection("AFC", AFC_DIVISIONS, saved_data)
    with col_nfc_s:
        nfc_seeds = render_seed_selection("NFC", NFC_DIVISIONS, saved_data)

    afc_complete = all(v != EMPTY_OPTION for v in afc_seeds.values())
    nfc_complete = all(v != EMPTY_OPTION for v in nfc_seeds.values())

    if not (afc_complete and nfc_complete):
        st.warning("⚠️ Bitte wähle alle Seeds (1–7) für AFC und NFC aus, um das Bracket zu aktivieren!")
        return

    st.markdown("---")
    st.success("✅ Seeds vollständig! Tippe nun die Playoff-Duelle:")

    bracket_picks = {}

    for conf_title, seeds in [("AFC Playoffs", afc_seeds), ("NFC Playoffs", nfc_seeds)]:
        conf_short = "AFC" if "AFC" in conf_title else "NFC"
        
        b_col1, b_col2 = st.columns([1, 10])
        with b_col1:
            st.image(CONF_LOGOS.get(conf_short), width=45)
        with b_col2:
            st.subheader(conf_title)

        team_to_seed = {team: seed_num for seed_num, team in seeds.items()}

        col_wc, col_div, col_conf = st.columns([1, 1, 1])

        with col_wc:
            st.markdown("**Wild Card Round**")
            k_wc1 = f"{conf_title}_wc1"
            k_wc2 = f"{conf_title}_wc2"
            k_wc3 = f"{conf_title}_wc3"

            wc1_winner = safe_radio(f"Match 1: #2 ({seeds[2]}) vs #7 ({seeds[7]})", [seeds[2], seeds[7]], k_wc1, saved_bracket_picks)
            wc2_winner = safe_radio(f"Match 2: #3 ({seeds[3]}) vs #6 ({seeds[6]})", [seeds[3], seeds[6]], k_wc2, saved_bracket_picks)
            wc3_winner = safe_radio(f"Match 3: #4 ({seeds[4]}) vs #5 ({seeds[5]})", [seeds[4], seeds[5]], k_wc3, saved_bracket_picks)

            bracket_picks[k_wc1] = wc1_winner
            bracket_picks[k_wc2] = wc2_winner
            bracket_picks[k_wc3] = wc3_winner

        # --- RE-SEEDING LOGIK FÜR DIVISIONAL ROUND ---
        wc_winners = [wc1_winner, wc2_winner, wc3_winner]
        wc_winners_sorted = sorted(wc_winners, key=lambda team: team_to_seed.get(team, 99))

        lowest_remaining_seed_team = wc_winners_sorted[-1]
        div_match_b_team1 = wc_winners_sorted[0]
        div_match_b_team2 = wc_winners_sorted[1]

        with col_div:
            st.markdown("**Divisional Round**")
            st.info(f"🏆 #1 Seed ({seeds[1]}) Bye-Week")
            
            k_div1 = f"{conf_title}_div1"
            k_div2 = f"{conf_title}_div2"

            div1_winner = safe_radio(
                f"Match A: #1 ({seeds[1]}) vs #{team_to_seed[lowest_remaining_seed_team]} ({lowest_remaining_seed_team})", 
                [seeds[1], lowest_remaining_seed_team], 
                k_div1,
                saved_bracket_picks
            )
            div2_winner = safe_radio(
                f"Match B: #{team_to_seed[div_match_b_team1]} ({div_match_b_team1}) vs #{team_to_seed[div_match_b_team2]} ({div_match_b_team2})", 
                [div_match_b_team1, div_match_b_team2], 
                k_div2,
                saved_bracket_picks
            )

            bracket_picks[k_div1] = div1_winner
            bracket_picks[k_div2] = div2_winner

        with col_conf:
            st.markdown("**Conference Championship**")
            k_final = f"{conf_title}_final"
            conf_champ = safe_radio(f"🏆 {conf_title} Finale:", [div1_winner, div2_winner], k_final, saved_bracket_picks)
            bracket_picks[k_final] = conf_champ
            st.success(f"Gewinner: **{conf_champ}**")

    st.markdown("---")
    st.subheader("🏈 SUPER BOWL FINALE")
    
    afc_finalist = bracket_picks.get("AFC Playoffs_final")
    nfc_finalist = bracket_picks.get("NFC Playoffs_final")

    if afc_finalist and nfc_finalist:
        sb_opts = [afc_finalist, nfc_finalist]
        
        # Super Bowl Gewinner wiederherstellen
        if "sb_winner_key" not in st.session_state:
            saved_sb = saved_data.get("super_bowl_winner")
            if saved_sb in sb_opts:
                st.session_state["sb_winner_key"] = saved_sb

        sb_curr = st.session_state.get("sb_winner_key")
        sb_idx = sb_opts.index(sb_curr) if sb_curr in sb_opts else 0
        
        super_bowl_champ = st.radio("Super Bowl Champion 2026:", options=sb_opts, index=sb_idx, key="sb_winner_key", disabled=is_locked())
        bracket_picks["sb_winner_key"] = super_bowl_champ

        sb_logo_url = TEAM_LOGOS.get(super_bowl_champ)
        if sb_logo_url:
            sb_col1, sb_col2 = st.columns([1, 4])
            with sb_col1:
                st.image(sb_logo_url, width=110)
            with sb_col2:
                st.markdown(f"### 🏆 Dein Super Bowl Champ: **{super_bowl_champ}**")

        st.markdown("---")
        btn_col1, btn_col2 = st.columns([1, 1])

        with btn_col1:
            if st.button("Playoff-Tipps speichern 🏆", use_container_width=True, disabled=is_locked()):
                playoff_exits = {}

                for conf_title in ["AFC Playoffs", "NFC Playoffs"]:
                    wc1_w = bracket_picks[f"{conf_title}_wc1"]
                    wc2_w = bracket_picks[f"{conf_title}_wc2"]
                    wc3_w = bracket_picks[f"{conf_title}_wc3"]

                    seeds = afc_seeds if "AFC" in conf_title else nfc_seeds
                    
                    for match_pair, winner in [([seeds[2], seeds[7]], wc1_w), ([seeds[3], seeds[6]], wc2_w), ([seeds[4], seeds[5]], wc3_w)]:
                        loser = [t for t in match_pair if t != winner][0]
                        playoff_exits[loser] = "Wild Card"

                    div1_w = bracket_picks[f"{conf_title}_div1"]
                    div2_w = bracket_picks[f"{conf_title}_div2"]
                    
                    # Wildcard-Sieger ermitteln
                    wc_w_sorted = sorted([wc1_w, wc2_w, wc3_w], key=lambda t: {team: s for s, team in seeds.items()}.get(t, 99))
                    lowest_seed_t = wc_w_sorted[-1]
                    
                    div_a_pair = [seeds[1], lowest_seed_t]
                    loser_div_a = [t for t in div_a_pair if t != div1_w][0]
                    playoff_exits[loser_div_a] = "Divisional Round"

                    div_b_pair = [wc_w_sorted[0], wc_w_sorted[1]]
                    loser_div_b = [t for t in div_b_pair if t != div2_w][0]
                    playoff_exits[loser_div_b] = "Divisional Round"

                    conf_champ_picked = bracket_picks[f"{conf_title}_final"]
                    conf_pair = [div1_w, div2_w]
                    conf_loser = [t for t in conf_pair if t != conf_champ_picked][0]
                    playoff_exits[conf_loser] = "Conference Championship"

                sb_runner_up = afc_finalist if super_bowl_champ == nfc_finalist else nfc_finalist
                playoff_exits[sb_runner_up] = "Super Bowl Runner-Up"

                # Alles dauerhaft in Google Sheets speichern
                saved_data["afc_seeds"] = afc_seeds
                saved_data["nfc_seeds"] = nfc_seeds
                saved_data["super_bowl_winner"] = super_bowl_champ
                saved_data["playoff_exits"] = playoff_exits
                saved_data["bracket_picks"] = bracket_picks
                
                save_data(user_key, saved_data)
                st.balloons()
                st.success(f"Dein Bracket wurde dauerhaft gespeichert! Super Bowl Champion: {super_bowl_champ}")

        with btn_col2:
            if is_locked():
                st.button("Playoff-Tipps zurücksetzen 🗑️", disabled=True, use_container_width=True)
            else:
                with st.popover("Playoff-Tipps zurücksetzen 🗑️", use_container_width=True):
                    st.markdown("**Was möchtest du zurücksetzen?**")
                    reset_afc = st.checkbox("AFC Seeds (1–7)")
                    reset_nfc = st.checkbox("NFC Seeds (1–7)")
                    reset_bracket = st.checkbox("Playoff Bracket & Super Bowl")

                    if st.button("Ausgewähltes löschen ⚠️", type="primary", use_container_width=True):
                        file_data = load_data(user_key)

                        if reset_afc:
                            file_data.pop("afc_seeds", None)
                            for pos in range(1, 8):
                                key = f"AFC_seed_{pos}"
                                if key in st.session_state:
                                    del st.session_state[key]

                        if reset_nfc:
                            file_data.pop("nfc_seeds", None)
                            for pos in range(1, 8):
                                key = f"NFC_seed_{pos}"
                                if key in st.session_state:
                                    del st.session_state[key]

                        if reset_bracket:
                            file_data.pop("super_bowl_winner", None)
                            file_data.pop("playoff_exits", None)
                            file_data.pop("bracket_picks", None)
                            for key in list(st.session_state.keys()):
                                if "Playoffs_" in key or "sb_winner" in key:
                                    del st.session_state[key]

                        save_data(user_key, file_data)
                        st.success("Ausgewählte Tipps wurden zurückgesetzt!")
                        st.rerun()

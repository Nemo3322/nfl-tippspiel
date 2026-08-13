import streamlit as st
from config import LOCK_DEADLINE, is_locked, CONF_LOGOS

def render_home_page():
    # Willkommens-Header
    st.title("🏈 NFL Tippspiel 2026")
    st.subheader(f"Willkommen zurück, {st.session_state['username'].capitalize()}!")

    st.markdown("---")

    # Status-Karte (Anzeigen, ob die Tipps offen oder geschlossen sind)
    col_status1, col_status2 = st.columns([1, 3])
    with col_status1:
        st.image(CONF_LOGOS.get("NFL"), width=100)
    with col_status2:
        if is_locked():
            st.error(f"🔒 **Status: Tippabgabe geschlossen**\n\nDie Abgabefrist ist seit dem **{LOCK_DEADLINE.strftime('%d.%m.%Y um %H:%M Uhr')}** abgelaufen.")
        else:
            st.success(f"🟢 **Status: Tippabgabe aktiv**\n\nDu kannst deine Tipps noch bis zum **{LOCK_DEADLINE.strftime('%d.%m.%Y um %H:%M Uhr')}** anpassen!")

    st.markdown("---")

    # Der Stand der Dinge / Anleitung
    st.subheader("📌 Der Stand der Dinge & Ablauf")

    col_info1, col_info2 = st.columns(2)

    with col_info1:
        st.markdown("""
        ### 1️⃣ Regular Season (Divisions)
        * Wähle auf den Seiten **AFC Tipps** und **NFC Tipps** die genauen Platzierungen (1–4) aller 8 Divisionen.
        * **Vergiss nicht**, unten auf den Speicher-Button zu klicken!
        """)

        st.markdown("""
        ### 2️⃣ Playoff Bracket & Super Bowl
        * Auf der Seite **Playoffs** ordnest du zuerst die Seeds (1–7) der Conferences.
        * Danach schaltet sich das interaktive **Playoff-Bracket** frei, bei dem du die Sieger bis zum Super Bowl Champ durchklicken kannst.
        """)

    with col_info2:
        st.markdown("""
        ### 3️⃣ Auswertung & Punkte
        * Sobald die Saison abgeschlossen ist, wertet der Admin die Ergebnisse aus.
        * Wer die meisten Punkte bei den Divisionen, Seeds, Playoff-Etappen und dem Super Bowl Champ sammelt, holt sich die **Trophäe**!
        """)

        st.markdown("""
        ### 🏆 Das Ziel
        * Schaffst du es ganz nach oben auf das Podest und sicherst dir einen Platz in der **Hall of Fame**?
        """)

    st.markdown("---")
    st.info("💡 **Tipp:** Nutze die Navigationsleiste auf der linken Seite, um zwischen den einzelnen Tipps, der Rangliste und den Regeln zu wechseln.")
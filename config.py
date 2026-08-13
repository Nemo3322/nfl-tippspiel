from datetime import datetime

LOCK_DEADLINE = datetime(2026, 9, 10, 2, 19)  # Beispiel: 5. September 2024, 23:59:59

def is_locked():
    """Überprüft, ob die Tippabgabe gesperrt ist."""
    return datetime.now() >= LOCK_DEADLINE


# Benutzer-Zugänge
USERS = {
    "mirco": "mirco1",
    "jan": "jan",
    "angelo": "angelo",
    "moritz": "moritz",
    "noel": "noel",
    "tim": "tim",
    "lenny": "lenny",
}

# Platzhalter für leere Felder
EMPTY_OPTION = "-- Bitte wählen --"

# Division-Teams
AFC_DIVISIONS = {
    "afc_north": ["Ravens", "Steelers", "Browns", "Bengals"],
    "afc_south": ["Texans", "Colts", "Jaguars", "Titans"],
    "afc_west": ["Chiefs", "Chargers", "Raiders", "Broncos"],
    "afc_east": ["Bills", "Dolphins", "Patriots", "Jets"]
}

NFC_DIVISIONS = {
    "nfc_north": ["Vikings", "Lions", "Packers", "Bears"],
    "nfc_south": ["Panthers", "Saints", "Falcons", "Buccaneers"],
    "nfc_west": ["49ers", "Rams", "Seahawks", "Cardinals"],
    "nfc_east": ["Giants", "Eagles", "Cowboys", "Commanders"]
}

# Team-Logos CDN Links
TEAM_LOGOS = {
    # AFC
    "Ravens": "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png",
    "Steelers": "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png",
    "Browns": "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png",
    "Bengals": "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png",
    "Texans": "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png",
    "Colts": "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png",
    "Jaguars": "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png",
    "Titans": "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png",
    "Chiefs": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
    "Chargers": "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png",
    "Raiders": "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png",
    "Broncos": "https://a.espncdn.com/i/teamlogos/nfl/500/den.png",
    "Bills": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
    "Dolphins": "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png",
    "Patriots": "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png",
    "Jets": "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png",
    # NFC
    "Packers": "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png",
    "Vikings": "https://a.espncdn.com/i/teamlogos/nfl/500/min.png",
    "Bears": "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png",
    "Lions": "https://a.espncdn.com/i/teamlogos/nfl/500/det.png",
    "Buccaneers": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png",
    "Saints": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png",
    "Falcons": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
    "Panthers": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png",
    "Seahawks": "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png",
    "49ers": "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png",
    "Cardinals": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png",
    "Rams": "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png",
    "Cowboys": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
    "Eagles": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png",
    "Giants": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png",
    "Commanders": "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png"
}

CONF_LOGOS = {
    "AFC": "https://a.espncdn.com/i/teamlogos/nfl/500/afc.png",
    "NFC": "https://a.espncdn.com/i/teamlogos/nfl/500/nfc.png",
    "NFL": "https://a.espncdn.com/i/teamlogos/nfl/500/nfl.png"
}

# --- PUNKTESYSTEM REGELN ---
POINTS_CONFIG = {
    "EXACT_DIVISION_POS": 2,    # Pro korrekt getippter Divisions-Platzierung
    "PLAYOFF_QUALIFIER": 5,     # Pro richtigem Playoff-Team (in Seeds 1-7 gelandet)
    "EXACT_SEED_POS": 10,       # Pro exakt richtigem Playoff-Seed (1-7)
    "EXACT_PLAYOFF_EXIT": 15,   # Pro Team, dessen Ausstiegsetappe exakt stimmt
    "SUPER_BOWL_WINNER": 25     # Für den richtigen Super Bowl Champion
}

# Datei für die Admin-Ergebnisse
OFFICIAL_RESULTS_FILE = "official_results.json"

# --- HALL OF FAME HISTORIE ---
HALL_OF_FAME = [
    {
        "Saison": "2025/2026",
        "Platz 1 🥇": "Angelo (92 Pkt)",
        "Platz 2 🥈": "Mirco (85 Pkt)",
        "Platz 3 🥉": "Tim (82 Pkt)",
        "PLatz 4": "Moritz (74 Pkt)",
        "Platz 5": "Noël (54 Pkt)",
        "Platz 6": "Jan (36 Pkt)"
    },
    {
        "Saison": "2024/2025",
        "Platz 1 🥇": "Angelo (134 Pkt)",
        "Platz 2 🥈": "Moritz (120 Pkt)",
        "Platz 3 🥉": "Mirco (114 Pkt)",
        "PLatz 4": "Tim (101 Pkt)",
        "Platz 5": "Jan (81 Pkt)"
    }
]
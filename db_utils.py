import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def get_clean_dataframe(conn):
    try:
        df = conn.read(worksheet="daten", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["key", "data"])
        
        # Nur echte Spalten 'key' und 'data' behalten
        if "key" not in df.columns or "data" not in df.columns:
            return pd.DataFrame(columns=["key", "data"])

        # Leere Zeilen und NaN-Werte vollständig entfernen
        df = df.dropna(subset=["key"]).copy()
        df["key"] = df["key"].astype(str).str.strip()
        df["data"] = df["data"].astype(str)
        df = df[df["key"] != ""]
        df = df[df["key"] != "nan"]
        return df
    except Exception:
        return pd.DataFrame(columns=["key", "data"])

def load_data(key_name):
    try:
        conn = get_connection()
        df = get_clean_dataframe(conn)
        if df.empty:
            return {}
        
        row = df[df["key"] == str(key_name).strip()]
        if not row.empty:
            raw_data = row.iloc[0]["data"]
            if raw_data and raw_data != "nan":
                return json.loads(raw_data)
    except Exception:
        return {}
    return {}

def save_data(key_name, data_dict):
    conn = get_connection()
    df = get_clean_dataframe(conn)
    
    clean_key = str(key_name).strip()
    data_json_str = json.dumps(data_dict)
    
    if clean_key in df["key"].values:
        # Bestehenden Eintrag überschreiben
        df.loc[df["key"] == clean_key, "data"] = data_json_str
    else:
        # Neuen Eintrag anhängen
        new_row = pd.DataFrame([{"key": clean_key, "data": data_json_str}])
        df = pd.concat([df, new_row], ignore_index=True)
        
    # Tabelle in Google Sheets sauber aktualisieren
    conn.update(worksheet="daten", data=df)
    st.cache_data.clear()

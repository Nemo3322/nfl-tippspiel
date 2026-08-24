import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json

def get_connection():
    # ttl=0 stellt sicher, dass Streamlit niemals veraltete Cache-Daten nutzt
    return st.connection("gsheets", type=GSheetsConnection, ttl=0)

def get_clean_dataframe(conn):
    try:
        df = conn.read(worksheet="daten", ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=["key", "data"])
        
        if "key" not in df.columns or "data" not in df.columns:
            return pd.DataFrame(columns=["key", "data"])

        df = df.dropna(subset=["key"]).copy()
        df["key"] = df["key"].astype(str).str.strip()
        df["data"] = df["data"].astype(str)
        df = df[df["key"] != ""]
        df = df[df["key"] != "nan"]
        return df
    except Exception:
        return pd.DataFrame(columns=["key", "data"])

def load_data(key_name):
    clean_key = str(key_name).strip()
    
    # 1. Schneller Abruf aus dem lokalen Session-Speicher (verhindert 30s Lücke)
    cache_key = f"cached_{clean_key}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    # 2. Aus Google Sheets laden
    try:
        conn = get_connection()
        df = get_clean_dataframe(conn)
        if df.empty:
            return {}
        
        row = df[df["key"] == clean_key]
        if not row.empty:
            raw_data = row.iloc[0]["data"]
            if raw_data and raw_data != "nan":
                parsed_data = json.loads(raw_data)
                # Im Session-State für die aktuelle Sitzung vormerken
                st.session_state[cache_key] = parsed_data
                return parsed_data
    except Exception:
        return {}
    return {}

def save_data(key_name, data_dict):
    clean_key = str(key_name).strip()
    
    # Sofort im lokalen Session-State aktualisieren -> Null Sekunden Wartezeit für den User!
    st.session_state[f"cached_{clean_key}"] = data_dict
    
    # Dauerhaft in Google Sheets schreiben
    try:
        conn = get_connection()
        df = get_clean_dataframe(conn)
        
        data_json_str = json.dumps(data_dict)
        
        if clean_key in df["key"].values:
            df.loc[df["key"] == clean_key, "data"] = data_json_str
        else:
            new_row = pd.DataFrame([{"key": clean_key, "data": data_json_str}])
            df = pd.concat([df, new_row], ignore_index=True)
            
        conn.update(worksheet="daten", data=df)
    except Exception as e:
        st.error(f"Fehler beim Speichern in Google Sheets: {e}")

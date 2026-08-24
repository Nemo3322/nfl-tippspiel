import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import json

def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def load_data(key_name):
    try:
        conn = get_connection()
        df = conn.read(worksheet="daten", ttl=0)
        if df.empty or "key" not in df.columns:
            return {}
        row = df[df["key"] == key_name]
        if not row.empty:
            raw_data = row.iloc[0]["data"]
            return json.loads(raw_data) if isinstance(raw_data, str) else {}
    except Exception:
        return {}
    return {}

def save_data(key_name, data_dict):
    conn = get_connection()
    df = conn.read(worksheet="daten", ttl=0)
    
    if df.empty or "key" not in df.columns:
        df = pd.DataFrame(columns=["key", "data"])

    data_json_str = json.dumps(data_dict)
    
    if key_name in df["key"].values:
        df.loc[df["key"] == key_name, "data"] = data_json_str
    else:
        new_row = pd.DataFrame([{"key": key_name, "data": data_json_str}])
        df = pd.concat([df, new_row], ignore_index=True)
        
    conn.update(worksheet="daten", data=df)

import streamlit as st
import requests

# Get keys from secrets
URL = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
KEY = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]

def add_contact(name, upi_id):
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates" # This is the "Upsert" logic
    }
    payload = {"name": name, "upi_id": upi_id}
    # We send a POST request to the 'contacts' table
    requests.post(f"{URL}/rest/v1/contacts", headers=headers, json=payload)

def get_all_contacts():
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}"
    }
    # We GET the data from the 'contacts' table
    response = requests.get(f"{URL}/rest/v1/contacts?select=name,upi_id", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return {row['name']: row['upi_id'] for row in data}
    return {}
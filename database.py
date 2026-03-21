import streamlit as st
import requests

URL = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
KEY = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]

# We now pass 'owner_vpa' (your UPI ID) to keep lists private
def add_contact(name, upi_id, owner_vpa):
    if not owner_vpa: return # Don't save if we don't know who owns it
    headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    
    # We save the 'user_id' so we know who this friend belongs to
    payload = {"name": name, "upi_id": upi_id, "user_id": owner_vpa}
    requests.post(f"{URL}/rest/v1/contacts", headers=headers, json=payload)

def get_all_contacts(owner_vpa):
    if not owner_vpa: return {}
    headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
    
    # We add a FILTER (?user_id=eq...) so you only see YOUR friends
    endpoint = f"{URL}/rest/v1/contacts?user_id=eq.{owner_vpa}&select=name,upi_id"
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return {row['name']: row['upi_id'] for row in data}
    return {}
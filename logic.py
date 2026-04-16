import hashlib
import requests
import streamlit as st

# Takes dictionary of each name, cost paid and scales the amount to match 
def proportional_tax(individual_share, total_bill_with_tax):

    subtotal = sum(individual_share.values())

    if subtotal == 0:
        return individual_share
    
    tax_multiplier = total_bill_with_tax / subtotal

    final_ledger = {
        name: max(0.00, round(amount * tax_multiplier, 2)) 
        for name, amount, in individual_share.items()
    }
    
    return final_ledger

def track_event_rest(event_name, vpa, num_friends, total, scaling_used):
    try:
        # Use a real string if vpa is None to prevent hashing errors
        vpa_str = str(vpa) if vpa else "no_vpa"
        user_id = hashlib.sha256(vpa_str.encode()).hexdigest()[:12]
        
        # Access secrets exactly how your database.py does
        url = f"{st.secrets["connections"]["supabase"]["SUPABASE_URL"]}/rest/v1/analytics_events"
        headers = {
            "apikey": st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
            "Authorization": f"Bearer {st.secrets["connections"]["supabase"]["SUPABASE_KEY"]}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        
        payload = {
            "event_name": event_name,
            "vpa_hash": user_id,
            "num_friends": int(num_friends),
            "total_amount": float(total),
            "used_scaling": bool(scaling_used)
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
            
    except Exception as e:
        pass
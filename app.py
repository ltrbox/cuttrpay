import streamlit as st
import logic
import services
import urllib.parse
from st_copy import copy_button


st.title("CuttrPay")

st.set_page_config(
    page_title="CuttrPay",
    page_icon="💸",
    layout="centered", # Keeps it looking like a mobile app
    initial_sidebar_state="collapsed" # Hides the messy settings sidebar
)

if "friends_list" not in st.session_state:
    st.session_state.friends_list = []

if "tax_ledger" not in st.session_state:
    st.session_state.tax_ledger = {}

final_ledger=0

unequal_ledger = {}

with st.sidebar:
    st.header("Settings")
    bill = st.number_input("Total Bill", min_value=0.0, value=100.0)
    vpa = st.text_input("Your UPI ID", placeholder="9876543210@ybl", help="Find this in GPay/PhonePe profile settings. Usually looks like 'name@bank' or 'number@bank'.")
    if not vpa:
        st.info("👆 Enter your UPI ID above to enable QR payments!")

    #Adding friends
    new_friend = st.text_input("Enter friend's name:", placeholder="e.g. Ronaldo")
    if st.button("Add Friend"):
        if new_friend and new_friend not in st.session_state.friends_list:
            st.session_state.friends_list.append(new_friend)
            st.session_state.tax_ledger = {}
            st.session_state.last_added = new_friend
            st.rerun()
        else:
            st.warning(f"{new_friend} already added")
    if "last_added" in st.session_state:
        st.success(f"✅ {st.session_state.last_added} added!")

    if st.button("Clear All Friends"):
        st.session_state.friends_list = []
        st.session_state.tax_ledger = {}
        st.rerun()

    event_name=st.text_input("Enter event name: ", placeholder="e.g. Restaurant/Trip")


st.write(f"Current Bill: Rs.{bill}")
st.write(f"Target VPA: {vpa}")

if st.session_state.friends_list:
    num_friends = len(st.session_state.friends_list)
    default_share = bill/num_friends if num_friends > 0 else 0.0

    st.subheader("Adjust individual shares")
    individual_share = {}

    for name in st.session_state.friends_list:
        amount = st.number_input(f"{name}'s share", value=float(default_share), key=f"input_{name}_{num_friends}")
        individual_share[name] = amount

    total_assigned = sum(individual_share.values())
    if abs(total_assigned - bill) > 0.1:
        st.warning(f"Note: Total assigned (₹{total_assigned:.2f}) doesn't match the bill (₹{bill:.2f}). Proportional tax will adjust this automatically!")
    

if st.button("Generate payment QR codes"):
    if st.session_state.friends_list:
        
        ledger = logic.proportional_tax(individual_share, bill)
        st.session_state.tax_ledger = ledger

        if vpa:
            services.qr_code_gen(ledger, vpa)
        else:
            st.warning("Skipping QR Code generation - No UPI ID provided")
        st.success("Scan Below")
        st.rerun()

upi_link = services.get_upi_link(vpa, bill)

if st.session_state.tax_ledger: 

    ledger = st.session_state.tax_ledger
    cols = st.columns(len(ledger))

    for i, (name, amount) in enumerate(ledger.items()):
        with cols[i]:
            st.metric(name, f"₹{amount:.2f}")
            img_path = f"qrs_output/{name}_owes_{amount:.2f}.png"
            st.image(img_path)
    
    for name, amount in ledger.items():
        personal_msg = f"Hey {name}! Your share for dinner is ₹{amount}. Pay here: {upi_link}"
    
        encoded_msg = urllib.parse.quote(personal_msg)
    
        st.link_button(f"📲 Send to {name}", f"https://wa.me/?text={encoded_msg}", use_container_width=True)

    summary_text = services.generate_summary(event_name, ledger)
    st.subheader("📋 Final Breakdown")
    st.code(summary_text, language="text")

    copy_button(summary_text, tooltip='Click to copy', copied_label='Copied!')


elif not st.session_state.friends_list:
    st.info("Add friends and hit 'Generate")


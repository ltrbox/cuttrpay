import streamlit as st
import database
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

if 'show_qrs' not in st.session_state:
    st.session_state.show_qrs = False

if "friends_list" not in st.session_state:
    st.session_state.friends_list = []

if "tax_ledger" not in st.session_state:
    st.session_state.tax_ledger = {}

if 'final_results' not in st.session_state:
    st.session_state.final_results = None

final_ledger=0

unequal_ledger = {}

with st.sidebar:
    st.title("CuttrPay")
    st.caption("v1 | ltrbox.labs@gmail.com")
    
    with st.expander("How it works"):
        st.write("1. Enter total bill.")
        st.write("2. Select or add friends.")
        st.write("3. Scan dynamic QRs to pay.")
        st.info("Add to Home Screen for instant access.")

    st.markdown("---")
    
    # --- 💰 SECTION 1: BILL SETTINGS ---
    st.header("1. Bill Details")
    bill = st.number_input("Total Amount (₹)", min_value=0.0, value=100.0, step=10.0)
    event_name = st.text_input("Event Name", placeholder="e.g. Lunch at Mess")

    # --- 💳 SECTION 2: RECEIVER SETTINGS ---
    st.header("2. Receiver UPI")
    vpa_prefix = st.text_input("Your ID", placeholder="e.g. 9876543210", value=st.session_state.get('saved_vpa_prefix', ""))
    
    handle = st.radio(
        "Handle:",
        ["@okaxis", "@ybl", "@paytm", "@ibl", "@okhdfcbank"],
        horizontal=True
    )
    vpa = f"{vpa_prefix}{handle}"
    st.caption(f"Paying to: **{vpa}**")

    st.markdown("---")

    # --- 📇 SECTION 3: THE MEMORY ENGINE (SQLite) ---
    st.header("3. Add Friends")
    
    new_friend = st.text_input("Quick Add (One-time)", placeholder="Enter name...", key="quick_add_input")
    if st.button("Add to Current Split", use_container_width=True):
        if new_friend and new_friend not in st.session_state.friends_list:
            # SAVE FIRST
            database.add_contact(new_friend, "", vpa)
            # UPDATE SESSION STATE IMMEDIATELY (Local Sync)
            st.session_state.friends_list.append(new_friend)
            st.toast(f"✅ {new_friend} added!")
            st.rerun()

    st.divider()

    # 2. FETCH FRESH DATA
    # Put this RIGHT BEFORE the multiselect to ensure it's the latest
    saved_contacts = database.get_all_contacts(vpa)
    
    if saved_contacts:
        selected = st.multiselect(
            "Select from Favorites:", 
            options=list(saved_contacts.keys()),
            placeholder="Choose friends..."
        )
        if st.button("Add Selected to Bill", type="primary", use_container_width=True):
            for name in selected:
                if name not in st.session_state.friends_list:
                    st.session_state.friends_list.append(name)
            st.rerun()

    # 3. MANAGEMENT
    with st.expander("⚙️ Manage & Add Favorites"):
        fav_name = st.text_input("Name", key="manage_fav_name")
        fav_upi = st.text_input("UPI ID (Optional)", key="manage_fav_upi")
        if st.button("Save to Cloud", key="save_fav_btn", use_container_width=True):
            if fav_name:
                database.add_contact(fav_name, fav_upi, vpa)
                st.toast(f"Saved {fav_name}!")
                # Force the refresh
                st.rerun()
        
        st.divider()
        # Re-fetch here specifically for the delete list
        if saved_contacts:
            for name in list(saved_contacts.keys()):
                col1, col2 = st.columns([4, 1])
                col1.write(name)
                if col2.button("🗑️", key=f"del_{name}"):
                    database.delete_contact(name, vpa)
                    st.rerun()

    # --- 🧹 Maintenance ---
    if st.session_state.friends_list:
        st.markdown("---")
        if st.button("Clear Current List", use_container_width=True):
            st.session_state.friends_list = []
            st.session_state.tax_ledger = {}
            st.rerun()

st.write("Open the sidebar on top - looks like >>")
st.write(f"Current Bill: Rs.{bill}")
st.write(f"Target VPA: {vpa}")

if st.session_state.friends_list:
    num_friends = len(st.session_state.friends_list)
    default_share = round(bill / num_friends, 2)

    st.subheader("Adjust individual shares")
    individual_share = {name: default_share for name in st.session_state.friends_list}

    for name in st.session_state.friends_list:
        amount = st.number_input(f"{name}'s share", value=float(default_share), key=f"input_{name}_{num_friends}")
        individual_share[name] = amount

    total_assigned = sum(individual_share.values())
    diff = round(bill-total_assigned, 2)
    if diff != 0:
        first_person = st.session_state.friends_list[0]
        individual_share[first_person] = round(individual_share[first_person] + diff, 2)

    if abs(total_assigned - bill) > 0.1:
        st.warning(f"Note: Total assigned (₹{total_assigned:.2f}) doesn't match the bill (₹{bill:.2f}). Proportional tax will adjust this automatically!")


if st.button("Generate payment QR codes"):
    st.session_state.show_qrs = True
    if st.session_state.friends_list:
        
        ledger = logic.proportional_tax(individual_share, bill)
        st.session_state.final_results = {name: max(0.0, amt) for name, amt in ledger.items()}

        st.session_state.tax_ledger = ledger
        for name, amount in st.session_state.tax_ledger.items():
            if vpa:
                if amount > 0:
                    services.qr_code_gen(ledger, vpa)
                else:
                    st.warning(f"Share for {name} is zero. No QR needed.")
            else:
                st.warning("Skipping QR Code generation - No UPI ID provided")
        st.success("Scan Below")
        st.rerun()

upi_link = services.get_upi_link(vpa, bill)

if st.session_state.final_results: 
    st.divider()
    res = st.session_state.final_results
    cols = st.columns(len(res))

    for i, (name, amount) in enumerate(res.items()):
        with cols[i]:
            st.metric(name, f"₹{amount:.2f}")
            if amount > 0:
                img_path = f"qrs_output/{name}_owes_{amount:.2f}.png"
                st.image(img_path, use_container_width=True)
            else:
                st.success("All Settled")
    
    for name, amount in st.session_state.tax_ledger.items():
        personal_msg = f"Hey {name}! Your share for dinner is ₹{amount}. Pay here: {upi_link}"
    
        encoded_msg = urllib.parse.quote(personal_msg)
    
        st.link_button(f"📲 Send to {name}", f"https://wa.me/?text={encoded_msg}", use_container_width=True)

    summary_text = services.generate_summary(event_name, individual_share)
    st.subheader("📋 Final Breakdown")
    st.code(summary_text, language="text")

    copy_button(summary_text, tooltip='Click to copy', copied_label='Copied!')


elif not st.session_state.friends_list:
    st.info("Add friends and hit 'Generate")

st.markdown("---") # Visual separator
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 0.8em;'>"
    "Have an idea or found a bug? 💡<br>"
    "<a href='mailto:ltrbox.labs@gmail.com' style='color: #007bff;'>ltrbox.labs@gmail.com</a>"
    "</div>", 
    unsafe_allow_html=True
)
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
    st.markdown("---")
    
    st.subheader("How it works")
    st.write("1. Enter total & names.")
    st.write("2. Show the dynamic QRs.")
    st.write("3. Friends scan & pay instantly - no sign up, only one phone needed (this)")
    
    st.info("Add this page to your Home Screen for instant access at lunch.")

    st.markdown("---")
    st.caption("Contact: ltrbox.labs@gmail.com")
    st.header("Settings")

    bill = st.number_input("Total Bill", min_value=0.0, value=100.0)
    st.write("### Who is receiving the money?")
    vpa_prefix = st.text_input("Your UPI ID (Before the @)", placeholder="e.g. 9876543210 or saish")

    # Create a row of chips for the most common Indian handles
    handle = st.radio(
        "Select your app handle:",
        ["@okaxis (GPay)", "@ybl (PhonePe)", "@paytm", "@ibl", "@okhdfcbank"],
        horizontal=True
    )

    # Strip the helper text to get the raw handle
    vpa_suffix = handle.split(" ")[0]
    vpa = f"{vpa_prefix}{vpa_suffix}"

    st.info(f"Payments will be directed to: **{vpa}**")
    
    if not vpa:
        st.info("👆 Enter your UPI ID above to enable QR payments!")

    #Adding friends
    new_friend = st.text_input("Enter friend's name: ", placeholder="e.g. Ronaldo")
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
                # Ensure the path matches exactly how you saved the file
                img_path = f"qrs_output/{name}_owes_{amount:.2f}.png"
                st.image(img_path, use_container_width=True)
            else:
                # The 'Aura' move: Show a checkmark for people who owe 0
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
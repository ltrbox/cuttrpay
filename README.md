# CuttrPay

**CuttrPay** is a minimalist, high-speed bill-splitting utility built for real-world social friction. 

Most splitting apps require everyone to have an account or the app. **CuttrPay** is different: only the bill-payer needs to open the website. It calculates proportional tax logic, generates instant UPI QR codes, and provides a ready-to-paste WhatsApp summary.
## Link
https://cuttrpay.streamlit.app/

## Key Features
- **Proportional Split:** Handles fixed individual shares while auto-balancing taxes and service charges.
- **Instant Settlement:** Generates dynamic UPI QR codes for immediate scan-and-pay.
- **Zero Friction:** No user accounts or downloads required for friends.
- **Social Integration:** One-click copy for WhatsApp group summaries.

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python 3.14+
- **QR Engine:** `qrcode` library

## Local Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/ltrbox/cuttrpay.git
   cd cuttrpay
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Run the app**
   ```python
   streamlit run app.py

# Developed by ltrbox

# services.py - Handles UPI string generation and QR code generation for that

import os
import qrcode
import shutil

def get_upi_link(vpa, amount):
    return f"upi://pay?pa={vpa}&am={amount}&cu=INR"

def qr_code_gen(final_ledger, vpa):
    # Overwrites the folder each time and starts new
    folder = "qrs_output"
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    for name, amount in final_ledger.items():
        if amount > 0: # only generates qr code if there is actual amount contributed
            # Build the string
            upi_link = f"upi://pay?pa={vpa}&pn={name}&am={amount:.2f}&cu=INR"
            
            # Create the QR image object
            img = qrcode.make(upi_link)
            
            # Save it using the name from dictionary
            img.save(f"qrs_output/{name}_owes_{amount:.2f}.png")
            
            print(f"Generated QR for {name}: ₹{amount}")

def generate_summary(event_name, shares):
    total = sum(shares.values())

    whale_name = max(shares, key=shares.get)
    whale_amount = shares[whale_name]
    
    summary = f"📊 *CuttrPay Summary: {event_name}*\n"
    summary += f" Total Bill: ₹{total}\n"
    summary += "---------------------------\n"
    
    for name, amount in shares.items():
        summary += f"• {name}: ₹{amount}\n"
    
    summary += "---------------------------\n"
    summary += f"🏆 Whale: {whale_name} (₹{whale_amount})\n"
    summary += "Generated via CuttrPay 🚀"
    return summary
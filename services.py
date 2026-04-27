# services.py - Handles UPI string generation and QR code generation for that

import os
import qrcode
import shutil
import urllib.parse


def get_upi_link(vpa, amount):
    return f"upi://pay?pa={vpa}&am={amount}&cu=INR"

def qr_code_gen(final_ledger, vpa):
    # Overwrites the folder each time and starts new
    folder = "qrs_output"
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

    safe_note = urllib.parse.quote("Sent via CuttrPay")
    for name, amount in final_ledger.items():
        if amount > 0: # only generates qr code if there is actual amount contributed
            safe_name = urllib.parse.quote(name)
            # Build the string
            upi_link = f"upi://pay?pa={vpa}&pn={safe_name}&am={amount:.2f}&cu=INR&tn={safe_note}"
            
            # Create the QR image object
            img = qrcode.make(upi_link)
            
            # Save it using the name from dictionary
            img.save(f"qrs_output/{name}_owes_{amount:.2f}.png")
            
            print(f"Generated QR for {name}: ₹{amount}")

def generate_summary(event_name, shares, bill_amount, ledger):
    max_amount = max(shares.values())

    whales = [name for name, amount in ledger.items() if amount == max_amount]
    summary = f"📊 *CuttrPay Summary: {event_name}*\n"
    summary += f" Total Bill: ₹{bill_amount}\n"
    summary += "---------------------------\n"
    
    for name, amount in ledger.items():
        summary += f"• {name}: ₹{amount}\n"
    
    summary += "---------------------------\n"
    return summary

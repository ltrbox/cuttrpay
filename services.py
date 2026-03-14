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
    max_amount = max(shares.values())

    whales = [name for name, amount in shares.items() if amount == max_amount]
    whale_amount = shares[whales]
    
    summary = f"📊 *CuttrPay Summary: {event_name}*\n"
    summary += f" Total Bill: ₹{total}\n"
    summary += "---------------------------\n"
    
    for name, amount in shares.items():
        summary += f"• {name}: ₹{amount}\n"
    
    summary += "---------------------------\n"

    if len(whales) == len(shares) and len(shares) > 1:
        summary += "🤝 It's an equal split! (Everyone's a Whale)"
    elif len(whales) > 1:
        summary += f"🏆 Joint Whales: {', '.join(whales)} (₹{max_amount} each)"
    else:
        summary += f"🏆 Whale: {whales[0]} (₹{max_amount})"
    summary += "Generated via CuttrPay 🚀"
    return summary
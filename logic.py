# logic.py - equal splitting and tax logic is done here

def equal_payment(bill_amount, num_friends, bill_ledger):
    num_friends = len(bill_ledger)
    share=bill_amount/num_friends
    for names in bill_ledger:
        print(f"{names} owes Rs.{share:.2f}\n Processing payment...")
    for name in bill_ledger:
        bill_ledger[name] = share
    return bill_ledger

# Takes dictionary of each name, cost paid and scales the tax to match 
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

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

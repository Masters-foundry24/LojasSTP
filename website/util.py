import decimal as de

def format_de(number):
    """
    In this function we format decimals so that they can be displayed properly
    in tables.

    Todo:
        -> Add full stops at each three digits for very large numbers.
        -> Round numbers with more decimals rather than truncate them.
    """
    number = str(number)
    number = number.replace(".", ",")
    if "," in number:
        pos = len(number) - number.index(",")
        if pos == 2: # One digit behind the decimal point.
            number = number + "0"
        elif pos == 3: # Two digits behind the decimal point.
            pass
        else: # cut off excess digits (rather than round them).
            number = number[:len(number) - (pos - 3)]
    else:
        number = number + ",00"

    if number.index(",") > 6 and number[0] != "-" or number.index(",") > 7:
        number = number[ : number.index(",") - 6] + "." + number[number.index(",") - 6 : number.index(",") - 3] + "." + number[number.index(",") - 3 : ]
    elif number.index(",") > 3 and number[0] != "-" or number.index(",") > 4:
        number = number[ : number.index(",") - 3] + "." + number[number.index(",") - 3 : ]
    return number

def compute_results(entries):
    """
    Computes statistics on profit in a given period based on a list of entries.
    """
    results = {
        "revenue": de.Decimal("0"),
        "gross_profit": de.Decimal("0"),
        "expenses": de.Decimal("0"),
        "net_profit": de.Decimal("0")
    }
    for e in entries:
        if e.entry_type == 1:
            results["revenue"] += de.Decimal(e.cash)
            results["gross_profit"] += de.Decimal(e.equity)
        elif e.entry_type in [3, 4]:
            results["expenses"] += de.Decimal(e.equity)
        if e.entry_type != 5:
            results["net_profit"] += de.Decimal(e.equity)
    results = {
        "revenue": format_de(results["revenue"]),
        "gross_profit": format_de(results["gross_profit"]),
        "expenses": format_de(results["expenses"]),
        "net_profit": format_de(results["net_profit"])
    }

    return results
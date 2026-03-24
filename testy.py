import time

curr_price = []
old_price = []
diff = []

def format_currency(amount):
    """Formats a float as a currency string (e.g., -$1,234.56)."""
    # Format the absolute value with commas and two decimal places
    formatted_amount = f"${abs(amount):,.2f}"
    # Prepend a minus sign if the original amount was negative
    if amount < 0:
        return f"-{formatted_amount}"
    return formatted_amount
def save_old_price(df):
    global curr_price
    global old_price
    global diff

    if old_price == []:
        curr_price = df
        old_price = curr_price
        diff = [
            format_currency(float(p) - float(old_price[j]))
            for j, p in enumerate(df)
        ]
        
    elif old_price != df:
        # print(df)
        # print(old_price)
        curr_price = df
        for i, newPrice in enumerate(df):
            if newPrice == 0:
                newPrice = old_price[i]
            elif newPrice != old_price[i]:
                if old_price[i] != 0:
                    diff[i] = format_currency(float(newPrice) - float(old_price[i]))
                old_price[i] = newPrice    
                    
                

    else:
        pass
    
    print("input = ")
    print(df)
    print("curr = ")
    print(curr_price)
    print("old_price")
    print(old_price)
    print("diff = ")
    print(diff)


    time.sleep(10)
    

test_list = [[125, 135, 0, 0],[0, 0, 10, 10],[20, 20, 10, 0],[0, 20, 10, 0],[0, 20, 10, 40]]

for list in test_list:
    save_old_price(list)
    print("============================================")

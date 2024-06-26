import Customer as cr

if __name__ == "__main__":
    test = cr.Customer("test",[],10)
    print(test.items_bought)
    test.buy_item(1,1)
    print(test.items_bought)
    test.buy_item(1,1)
    print(test.items_bought)
    test.buy_item(2,1)
    print(test.items_bought)
    test.buy_item(3,10)
    print(test.items_bought)
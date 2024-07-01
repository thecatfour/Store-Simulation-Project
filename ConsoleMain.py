import StoreSimulator as sim

def create_random_customer_list(store: sim.StoreSimulator, customer_count: int = 100, max_money: int = 500, max_items: int = 10) -> list:
    """
    Creates a list of customers for the inputted store.
    """

    output = []

    for _ in range(customer_count):
        output.append(store.generate_random_customer(max_money, max_items))

    return output



def reset_customers(customer_list: list):
    """
    Resets each customer in the customer list.
    """

    for customer in customer_list:
        customer.reset_customer()



def print_options(current_day: int):
    print("Options:\n")
    print("1: Simulate next day (Day " + str(current_day + 1) + ")")
    print("2: Get income for current day (Day " + str(current_day) + ")")
    print("3: Get item")
    print("4: Get items with low stock")
    print("5: Add stock to one item")
    print("6: Add stock to all low stock items")
    print("7: Create updated stock csv")
    print("8: Clear store directory")
    print("q: Quit\n")



if __name__ == "__main__":
    # Set up the store for the simulation
    print("\nStore Simulator Console\n")

    item_database = "ItemList.csv"
    start_hour = 9
    end_hour = 18
    action_interval_in_mins = 5
    verbose = False
    store_name = "New Store"

    store = sim.StoreSimulator(item_database, start_hour, end_hour, action_interval_in_mins, verbose, store_name)

    print("Starting store attributes: \n")
    print("Store Name:          " + store_name)
    print("Item Database:       " + item_database)
    print("Opening Hour:        " + store.minutes_to_time(start_hour * 60))
    print("Closing Hour:        " + store.minutes_to_time(end_hour * 60))
    print("Minutes per Action:  " + str(action_interval_in_mins) + "\n")

    # Create a customer list for the simulation
    customer_list = create_random_customer_list(store, 100)

    # Wait for user
    user_input = input("Enter anything to continue: ")

    print()

    # Loop for executing the simulation
    while(True):
        
        print("\n" + store.store_name + " is on Day " + str(store.day))
        print_options(store.day)
        user_input = input("Enter selection: ")
        print()
        
        match str(user_input):
            case "1":
                # Reset customers
                reset_customers(customer_list)
                # Simulate one day
                store.simulate_one_day(customer_list.copy(), False, 0.1, 3)
                # Output to csv files
                store.output_stock()
                store.output_transactions()
            case "2":
                # Get income for this day
                print("Day " + str(store.day) + " Income: " + str(store.get_income_for_current_day()))
                user_input = input("Enter anything to continue: ")
                print()
            case "3":
                # Get item
                while(True):
                    user_input = input("Enter item id or 'q' to return to options: ")
                    if str(user_input) == "q":
                        break
                    
                    print()
                    print(store.get_item(int(user_input)))
                    print()
            case "4":
                # Get items with low stock
                while(True):
                    user_input = input("Enter threshold for item stock or 'q' to return to options: ")
                    if str(user_input) == "q":
                        break

                    try:
                        print(store.get_low_stock(int(user_input)))
                    except:
                        print("The input '" + user_input + "' is not an integer.")
            case "5":
                # Add stock to one item
                while(True):
                    user_input = input("Enter item id to add stock to or 'q' to return to options: ")
                    if str(user_input) == "q":
                        break

                    try:
                        temp = store.get_item(int(user_input))

                        print()
                        print(temp)
                        print()
                    except ValueError:
                        print("The input '" + user_input + "' is not an integer.")
                        continue

                    if temp.empty:
                        print("Item id '" + user_input + "' does not exist.")
                        continue
                    
                    # See how much stock should be added
                    while(True):
                        user_input = input("Enter amount of stock to add or 'q' to return to inserting item id: ")
                        if str(user_input) == "q":
                            break

                        try:
                            index = temp.index.item()

                            # Modify temp dataframe to output to user
                            temp.at[index, "Stock"] = temp.at[index, "Stock"] + int(user_input)

                            # Modify real dataframe
                            store.add_stock(temp.at[index, "Item Id"], int(user_input))

                            print("\nNew stock:")
                            print(temp)
                            print()
                        except ValueError:
                            print("The input '" + user_input + "' is not an integer.")
                            continue
                    del temp
                    del index
            case "6":
                # Add stock to all low stock items
                while(True):
                    user_input = input("Enter threshold for item stock or 'q' to return to options: ")
                    if str(user_input) == "q":
                        break

                    try:
                        temp = store.get_low_stock(int(user_input))

                        print()
                        print(temp)
                        print()
                    except ValueError:
                        print("The input '" + user_input + "' is not an integer.")
                        continue

                    if temp.empty:
                        print("There are no items with less than '" + user_input + "' stock.")
                        continue
                    
                    # See how much stock should be added
                    while(True):
                        user_input = input("Enter amount of stock to add or 'q' to return to inserting item id: ")
                        if str(user_input) == "q":
                            break

                        try:
                            for index in temp.index:
                                # Modify temp dataframe to output to user
                                temp.at[index, "Stock"] = temp.at[index, "Stock"] + int(user_input)

                                # Modify real dataframe
                                store.add_stock(temp.at[index, "Item Id"], int(user_input))

                            print("\nNew stock:")
                            print(temp)
                            print()
                        except ValueError:
                            print("The input '" + user_input + "' is not an integer.")
                            continue
                    del temp
            case "7":
                # Create updated stock csv
                print("Creating updated stock csv...")
                store.output_updated_stock()
            case "8":
                # Clear store directory
                print("Warning: This will delete all .csv files in the folder '" + store.store_name + "'.")
                user_input = input("\nEnter 'y' to confirm deletion: ")
                if user_input == "y" or user_input == "Y":
                    store.clear_store_directory()
            case "q":
                exit()
            case "Q":
                exit()
            case "c":
                # Hidden debug option
                user_input = input("Customer Name: ")
                for customer in customer_list:
                    if customer.name == user_input:
                        print(customer)
                        break
            case _:
                print("Invalid selection.")
        
        
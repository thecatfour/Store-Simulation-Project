import Customer as cr

import pandas as pd
import random as rand

class StoreSimulator:

    # Used when determining what action a customer will take
    # Sum should be 100 for 100%
    LOOK_CHANCE = 60
    BUY_CHANCE = 35
    LEAVE_CHANCE = 5
    
    def __init__(self, file_name: str, start_hour: float, end_hour: float, action_interval_minutes: int):
        self.item_dataframe = pd.read_csv(file_name)
        
        # Translates the tags into a list
        self.item_dataframe["Tags"] = self.item_dataframe["Tags"].str.split(", ")
        
        # Set up time related fields
        if start_hour < 0:
            self.start_hour = 0
        elif start_hour > 24:
            self.start_hour = 24
        else:
            self.start_hour = start_hour

        if end_hour < 0:
            self.end_hour = 0
        elif end_hour > 24:
            self.end_hour = 24
        else:
            self.end_hour = end_hour

        # If start hour occurs after end hour, change to back-up values
        if self.start_hour > self.end_hour:
            self.start_hour = 9
            self.end_hour = 17

        self.current_minute = self.start_hour * 60
        self.day = 1

        # Action interval is in minutes
        self.action_interval_minutes = action_interval_minutes

        # Set up customers list, which is used to output a csv file on data regarding the store
        # An entry should be "transaction id, customer name, items, money spent, time entered, time left"
        self.customer_transactions = []

        # Customers dict for which customers are in the store
        self.customers_in_store = {}

        self.next_transaction_id = 0

    def customer_enters(self, customer: cr.Customer):
        # Check if customer with same name is in the store
        # If the customer already exists, create a new object with a "?" added
        if customer.name in self.customers_in_store:
            print("Warning: customer '" + customer.name + "' is already in the store. Adding '?' to name.")
            customer = cr.Customer(customer.name + " ?", customer.item_tags, customer.money, customer.max_items)
        
        customer.set_enter(self.current_minute)
        self.customers_in_store[customer.name] = customer

    def customer_leaves(self, customer: cr.Customer):
        # Create an entry in customer transactions
        self.customer_transactions.append([str(self.next_transaction_id), customer.name, self.__translate_items_bought(customer.items_bought), "$" + "{:.2f}".format(customer.get_money_difference()), 
                                           StoreSimulator.minutes_to_time(customer.enter), StoreSimulator.minutes_to_time(self.current_minute)])
        
        # Remove that customer from the dict
        self.customers_in_store.pop(customer.name)

        # Reset their item transactions
        customer.reset_items()

        # Increment transaction id
        self.next_transaction_id += 1

    def customer_action(self, customer: cr.Customer):
        # Check if customer wants to buy something
        if customer.wants_more_items():
            # Use rand to determine an action that the customer will take
            choice = rand.randint(0, StoreSimulator.LOOK_CHANCE + StoreSimulator.BUY_CHANCE + StoreSimulator.LEAVE_CHANCE - 1)
            
            if choice < StoreSimulator.LOOK_CHANCE:
                # Customer does nothing
                # Buy amounts slightly decreases to keep customers from staying too long
                customer.decrease_buy_attempts(0.2)
            elif choice < StoreSimulator.BUY_CHANCE + StoreSimulator.LOOK_CHANCE:
                # Customer tries to buy something
                ...
            else:
                # Customer decides to leave
                self.customer_leaves(customer)
        else:
            # Customer leaves as they want nothing else
            self.customer_leaves(customer)


    def __translate_items_bought(self, customer_dict: dict) -> list:
        output = []
        name_column = self.item_dataframe.Name
        for key in customer_dict:
            output.append("Id:" + str(key) + " Name:" + name_column[key] + " Quantity:" + str(customer_dict[key]))
        return output
    
    def check_if_name_in_store(self, name: str) -> bool:
        return name in self.customers_in_store
    
    @staticmethod
    def minutes_to_time(minutes: int) -> str:
        return str(int(minutes / 60)) + ":" + str(int(minutes % 60))


if __name__ == "__main__":
    print("Simulator Testing\n")
    
    test_sim = StoreSimulator("ItemList.csv",6.5,18,5)

    testCust = cr.Customer()

    test_sim.customer_enters(testCust)
    test_sim.customer_enters(testCust)

    testCust.buy_item(1,5)

    test_sim.customer_leaves(testCust)
    test_sim.customer_enters(testCust)
    test_sim.customer_leaves(testCust)

    df = pd.DataFrame(test_sim.customer_transactions,columns=["one","two","three","four","five","six"])

    df.to_csv("out.csv",index=False)

    print(df)

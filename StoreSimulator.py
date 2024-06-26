import Customer as cr

import pandas as pd
import random as rand

class StoreSimulator:
    
    def __init__(self, file_name: str, start_hour: int, end_hour: int, action_interval_minutes: int):
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
            customer = cr.Customer(customer.name + " ?", customer.item_tags, customer.money, customer.max_items)
        
        self.customers_in_store[customer.name] = customer

    def customer_leaves(self):
        pass


if __name__ == "__main__":
    print("Simulator Testing\n")
    
    test_sim = StoreSimulator("ItemList.csv",6,18,5)

    testCust = cr.Customer()

    test_sim.customer_enters(testCust)
    test_sim.customer_enters(testCust)

    print(testCust)

    for value in test_sim.customers_in_store.values():
        print(value)
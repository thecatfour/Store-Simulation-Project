import Customer as cr

import pandas as pd
import random as rand

class StoreSimulator:

    # Used when determining what action a customer will take
    LOOK_CHANCE = 0.6
    BUY_CHANCE = 0.35
    LEAVE_CHANCE = 0.05
    


    def __init__(self, file_name: str, start_hour: float, end_hour: float, action_interval_minutes: int, verbose: bool = False):
        self.item_dataframe = pd.read_csv(file_name)

        # Check if each item has a unique item id

        temp = set()

        for row in self.item_dataframe.iterrows():
            if row[1]["Item Id"] in temp:
                raise SyntaxError("Item Id '" + str(row[1]["Item Id"]) + "' occurs multiple times. Each Id must be unique.\n\nDuplicate Item Id Entry:\n\n" + str(row[1]))
            else:
                temp.add(row[1]["Item Id"])
        
        del temp
        
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
        self.day = 0

        # Action interval is in minutes
        self.action_interval_minutes = action_interval_minutes

        # Set up customers list, which is used to output a csv file on data regarding the store
        # An entry should be "transaction id, customer name, items, money spent, time entered, time left"
        self.customer_transactions = []

        # Customers dict for which customers are in the store
        self.customers_in_store = {}

        # Internal dict to group what items belong to what groups
        self.item_groups = {}

        self.__init_item_groups()

        self.next_transaction_id = 0

        # Debugging tool to print when customers do stuff
        self.verbose = verbose



    def customer_enters(self, customer: cr.Customer):
        # Check if customer with same name is in the store
        # If the customer already exists, create a new object with a "?" added
        if customer.name in self.customers_in_store:
            print("Warning: customer '" + customer.name + "' is already in the store. Adding '?' to name.")
            customer = cr.Customer(customer.name + " ?", customer.item_tags, customer.money, customer.max_buy_attempts)
        
        customer.set_enter(self.current_minute)
        self.customers_in_store[customer.name] = customer

        if(self.verbose):
            print("Enter: " + customer.name + " at " + self.minutes_to_time(self.current_minute) + ".")



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

        if(self.verbose):
            print("Leave: " + customer.name + " at " + self.minutes_to_time(self.current_minute) + ".")



    def customer_action(self, customer: cr.Customer):
        # Check if customer wants to buy something
        if customer.wants_more_items():
            # Use rand to determine an action that the customer will take
            choice = rand.random()

            if choice < StoreSimulator.LOOK_CHANCE:
                # Customer does nothing

                # Buy amount slightly decreases to keep customers from staying too long
                customer.decrease_buy_attempts(0.2)
            elif choice < StoreSimulator.BUY_CHANCE + StoreSimulator.LOOK_CHANCE:
                # Customer tries to buy something
                
                potential_buys = self.__get_customer_potential_buys(customer)
        
                # If list is empty, there is nothing left to buy or nothing the customer wants, so they leave
                if potential_buys == []:
                    self.customer_leaves(customer)
                    return
                
                # Use rand to determine an item that the customer will buy
                choice = rand.randint(0, len(potential_buys) - 1)

                # See if customer buys the item
                # Will be true if the item is bought
                if customer.buy_item(potential_buys[choice][0], potential_buys[choice][1]):
                    # Get index of row using the item id
                    row_index = self.item_dataframe.index.get_loc(self.item_dataframe[self.item_dataframe["Item Id"] == potential_buys[choice][0]].index[0])

                    # Change the stock
                    self.item_dataframe.at[row_index,"Stock"] = self.item_dataframe.at[row_index,"Stock"] - 1

                if(self.verbose):
                    print("Buy: " + customer.name + " tried to buy Id:" + str(potential_buys[choice][0]) + " at " + self.minutes_to_time(self.current_minute) + ".")

                del potential_buys
                return
            else:
                # Customer decides to leave
                self.customer_leaves(customer)
                return
        else:
            # Customer leaves as they want nothing else
            self.customer_leaves(customer)
            return



    def do_action_interval(self) -> bool:
        # Check if the store should close
        if self.current_minute > self.end_hour * 60:
            # Loop through each customer and force them to leave
            for customer in self.customers_in_store:
                self.customer_leaves(customer)
            return False

        # Loop through each customer in the store and call customer action for them
        for customer in self.customers_in_store:
            self.customer_action(customer)

        # Add action interval to the current minutes
        self.current_minute = self.current_minute + self.action_interval_minutes

        # If the store is still open (current minutes is less than end time), then return true
        return True



    def start_new_day(self):
        # Delete old data structures and create new ones
        del self.customer_transactions
        del self.customers_in_store

        self.customer_transactions = []
        self.customers_in_store = {}

        # Increase day counter
        self.day = self.day + 1

        # Reset current minutes
        self.current_minute = self.start_hour * 60


    
    def simulate_one_day(self, customer_list: list = [], use_random_customers: bool = False, customer_enter_chance: float = 0.1, customer_enter_max: int = 3):
        # Start a new day
        self.start_new_day()

        print("Day " + str(self.day) + " begins.")

        # Allows customers to enter at the start hour
        self.current_minute = self.current_minute - self.action_interval_minutes

        # Loop through the day
        while(self.do_action_interval()):
            # Check if customers enter
            if rand.random() < customer_enter_chance:
                customers_enter_count = rand.randint(1, customer_enter_max)

                # Check how to add customers to the store
                if len(customer_list) > customers_enter_count:
                    # Add randomly generated amount of customers from customer list to store
                    while(customers_enter_count > 0):
                        self.customer_enters(customer_list.pop(rand.randint(0, len(customer_list) - 1)))
                        customers_enter_count = customers_enter_count - 1
                elif len(customer_list) != 0:
                    # Add rest of customer list to store
                    while(len(customer_list) > 0):
                        self.customer_action(customer_list.pop())
                elif use_random_customers:
                    # Add randomly generated customers to store
                    while(customers_enter_count > 0):
                        self.customer_enters(self.generate_random_customer())
                        customers_enter_count = customers_enter_count - 1
        
        # Day is over
        print("Day " + str(self.day) + " ends.")



    def generate_random_customer(self) -> cr.Customer:
        pass



    def __translate_items_bought(self, customer_dict: dict) -> list:
        output = []
        name_column = self.item_dataframe.Name

        # Create a list of all items bought so all bought items can be stored in a single column
        for key in customer_dict:
            output.append("Id:" + str(key) + " Name:" + name_column[key] + " Quantity:" + str(customer_dict[key]))
        
        del name_column

        return output
    


    def __init_item_groups(self):
        # Set up the "Any" group
        self.item_groups["Any"] = set()

        # Initialize item groups by going through entire item dataframe
        for row in self.item_dataframe.iterrows():
            # Add each item to the "Any" group
            self.item_groups["Any"].add(row[1]["Item Id"])

            # Check each tag in any item
            for tag_str in row[1]["Tags"]:
                if tag_str in self.item_groups:
                    self.item_groups[tag_str].add(row[1]["Item Id"])
                else:
                    self.item_groups[tag_str] = {row[1]["Item Id"]}



    def __get_customer_potential_buys(self, customer: cr.Customer) -> list:
        # Add every item in the input dataframe into a list
        output = []

        if "Any" in customer.item_tags:
            # Transverse the dataframe
            for row in self.item_dataframe.iterrows():
                if row[1]["Stock"] > 0:
                    for weight in range(0, row[1]["Weight"]):
                        output.append([row[1]["Item Id"], row[1]["Cost (USD)"]])
        else:
            # Create set using item groups to determine potential buys
            items_to_loc = set()

            # Get all ids of the wanted items
            for customer_tag in customer.item_tags:
                items_to_loc = items_to_loc.union(self.item_groups[customer_tag])

            # Check if the set is empty
            if len(items_to_loc) == 0:
                # The customer's tags do not match with anything in the item list, so they leave
                del items_to_loc
                return []

            # Get the rows from the item dataframe of the wanted items
            items = self.item_dataframe.loc[self.item_dataframe["Item Id"].isin(items_to_loc)]

            # Transverse the dataframe
            for row in items.iterrows():
                if row[1]["Stock"] > 0:
                    for weight in range(0, row[1]["Weight"]):
                        output.append([row[1]["Item Id"], row[1]["Cost (USD)"]])

            del items
            del items_to_loc

        return output
    

    
    def check_if_name_in_store(self, name: str) -> bool:
        return name in self.customers_in_store
    


    @staticmethod
    def minutes_to_time(minutes: int) -> str:
        return str(int(minutes / 60)) + ":" + str(int(minutes % 60))


# Test function for when this file is run

if __name__ == "__main__":
    print("Simulator Testing\n")
    
    test_sim = StoreSimulator("ItemList.csv",6.5,18,5,True)

    testCust = cr.Customer("Cust1",["Fruit","Clothes"],20,5)

    test_sim.customer_enters(testCust)
    test_sim.customer_enters(cr.Customer())

    test_sim.customer_action(testCust)

    print(test_sim.item_dataframe)

    """     testCust.buy_item(1,5)

    test_sim.customer_leaves(testCust)
    test_sim.customer_enters(testCust)
    test_sim.customer_leaves(testCust) """

    #df = pd.DataFrame(test_sim.customer_transactions,columns=["one","two","three","four","five","six"])

    #df.to_csv("out.csv",index=False)

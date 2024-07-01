import os
import glob

import pandas as pd
import random as rand
import Customer as cr

from ast import literal_eval

class StoreSimulator:
    # Used when determining what action a customer will take
    LOOK_CHANCE = 0.6
    BUY_CHANCE = 0.37
    LEAVE_CHANCE = 0.03
    
    # Used to create a directory for all output files
    OUTPUT_DIR_NAME = "Store Simulator Output Files"


    def __init__(self, file_name: str, start_hour: float, end_hour: float, action_interval_minutes: int, verbose: bool = False, store_name: str = "Default Name"):
        """
        Initializes a Store Simulator object.

        file_name: The path to a csv of items along with other necessary data. See "ItemList.csv" for an example of correct formatting.

        start_hour: The hour that the store opens and the earliest that customers can arrive.

        end_hour: The hour that the store closes and forces all customers to leave.

        action_inverval_minutes: The amount of time added to the current time during an action interval. Larger values mean fewer actions in a day.

        verbose: Prints more data to the console such as customers entering, buying, and leaving.

        store_name: The name given to the store for output files.
        """

        # Set up fields related to the item list
        
        self.item_dataframe = None
        self.item_groups = None
        self.item_group_names = None

        self.set_item_list(file_name)
        
        # Set up start hour
        if start_hour < 0:
            self.start_hour = 0
        elif start_hour > 24:
            self.start_hour = 24
        else:
            self.start_hour = start_hour

        # Set up end hour
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
        self.item_group_names = []

        self.__init_item_groups()

        self.next_transaction_id = 0

        # Debugging tool to print when customers do stuff
        self.verbose = verbose

        # Used to generate random customers
        self.__random_cust_id = 0

        self.store_name = store_name



    def customer_enters(self, customer: cr.Customer):
        """
        Puts the input customer into the store's dictionary of customers.
        """

        # Check if customer with same name is in the store
        # If the customer already exists, create a new object with a "?" added
        if customer.name in self.customers_in_store:
            print("Warning: customer '" + customer.name + "' is already in the store. Adding '?' to name.")
            customer = cr.Customer(customer.name + " ?", customer.item_tags, customer.money, customer.max_buy_attempts)
        
        customer.set_enter(self.current_minute)
        self.customers_in_store[customer.name] = customer

        if(self.verbose):
            print(self.minutes_to_time(self.current_minute) + " Enter: " + customer.name + "            Store: " + self.store_name)



    def public_customer_leaves(self, customer: cr.Customer):
        """
        Public version of customer leaves.
        This should only be called with an input customer that is in the store.
        """

        if self.check_if_name_in_store(customer.name):
            self.__customer_leaves(customer)
        else:
            raise ValueError("Customer '" + customer.name + "' is not in the store '" + self.store_name + "'.")
        


    def __customer_leaves(self, customer: cr.Customer):
        """
        Removes the input customer from the store's dictionary of customers and adds a record to customer transactions.
        """

        # Create an entry in customer transactions
        self.customer_transactions.append([str(self.next_transaction_id), customer.name, self.__translate_items_bought(customer.items_bought), "{:.2f}".format(customer.get_money_difference()), 
                                           self.minutes_to_time(customer.enter), self.minutes_to_time(self.current_minute)])
        
        # Remove that customer from the dict
        self.customers_in_store.pop(customer.name)

        # Reset their item transactions
        customer.reset_items()

        # Increment transaction id
        self.next_transaction_id += 1

        if(self.verbose):
            print(self.minutes_to_time(self.current_minute) + " Leave: " + customer.name  + "           Store: " + self.store_name)



    def public_customer_action(self, customer: cr.Customer):
        """
        Public version of customer action.
        This should only be called with an input customer that is in the store.
        """

        if self.check_if_name_in_store(customer.name):
            self.__customer_action(customer)
        else:
            raise ValueError("Customer '" + customer.name + "' is not in the store '" + self.store_name + "'.")



    def __customer_action(self, customer: cr.Customer):
        """
        Makes the input customer buy something, do nothing, or leave the store.
        """
        
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
                    self.__customer_leaves(customer)
                    return
                
                # Use rand to determine an item that the customer will buy
                choice = rand.randint(0, len(potential_buys) - 1)

                # See if customer buys the item
                # Will be true if the item is bought
                if customer.buy_item(potential_buys[choice][0], potential_buys[choice][1]):
                    # Get index of row using the item id
                    row_index = self.get_row_index("Item Id", potential_buys[choice][0])

                    # Change the stock
                    self.item_dataframe.at[row_index, "Stock"] = self.item_dataframe.at[row_index, "Stock"] - 1

                if(self.verbose):
                    print(self.minutes_to_time(self.current_minute) + " Buy: " + customer.name + " tried to buy Id:" + str(potential_buys[choice][0]) + "           Store: " + self.store_name)

                del potential_buys
                return
            else:
                # Customer decides to leave
                self.__customer_leaves(customer)
                return
        else:
            # Customer leaves as they want nothing else
            self.__customer_leaves(customer)
            return



    def do_action_interval(self) -> bool:
        """
        Store progresses the amount of time of its action_interval_minutes.
        """
        
        # Add action interval to the current minutes
        self.current_minute = self.current_minute + self.action_interval_minutes

        # Check if the store should close
        if self.current_minute >= self.end_hour * 60:
            # Loop through each customer and force them to leave
            for customer in self.customers_in_store.copy():
                self.__customer_leaves(self.customers_in_store[customer])
            return False

        # Loop through each customer in the store and call customer action for them
        for customer in self.customers_in_store.copy():
            self.__customer_action(self.customers_in_store[customer])

        # If the store is still open (current minutes is less than end time), then return true
        return True



    def start_new_day(self):
        """
        Resets data structures and increments day counter.
        """

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
        """
        Simulates one day of operation for the store object.

        customer_list: List of specific customers that should enter the store before any random customers.

        use_random_customers: Determines if the store should generate random customers if the customer_list is empty.

        customer_enter_chance: The chance that a customer enters the store at every action interval.

        customer_enter_max: The max amount of customers that can enter the store at any action interval.
        """

        # Start a new day
        self.start_new_day()

        print("Store: " + self.store_name + " Day " + str(self.day) + " begins.\n")

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
                        self.customer_enters(customer_list.pop())
                elif use_random_customers:
                    # Add randomly generated customers to store
                    while(customers_enter_count > 0):
                        self.customer_enters(self.generate_random_customer())
                        customers_enter_count = customers_enter_count - 1
        
        # Day is over
        print("\nStore: " + self.store_name + " Day " + str(self.day) + " ends.")

        del customer_list



    def generate_random_customer(self, money_multiplier: int = 200, max_items_multiplier: int = 20) -> cr.Customer:
        """
        Generates a random customer based on the store's item database.

        money_multiplier: Multiplies random() to create a balance for an individual customer. Max money will be money_multiplier plus a small constant.

        max_items_multiplier: Multiplies random() to create a max value of items the customer can buy. Max items will be max_items_multiplier plus a small constant.
        """

        customer = cr.Customer("Rand Cust " + str(self.__random_cust_id))
        self.__random_cust_id = self.__random_cust_id + 1

        # Determine how many tags to give the customer from 1 to half of the tags avaliable
        # Note: randomly generated customers cannot have the "Any" tag
        tag_count = rand.randint(1, int(len(self.item_group_names) / 2))

        new_tags = []

        # Give tags to customer
        for _ in range(tag_count):
            # Get index of random tag
            index = rand.randint(0, len(self.item_group_names) - 1)

            tag = self.item_group_names[index]

            # Only add the tag if it is not already in the lsit
            if tag not in new_tags:
                new_tags.append(tag)

        customer.set_tags(new_tags)
        del new_tags

        customer.set_money(rand.random() * money_multiplier + 5.00)
        customer.set_max_buy_attempts(rand.random() * max_items_multiplier + 1)

        if rand.random() >= 0.5:
            customer.using_credit = True
        else:
            customer.using_credit = False

        return customer
    


    def output_transactions(self):
        """
        Outputs customer_transactions to a directory specific to the store.
        """
        
        # Make the name of the file
        output_file_name = self.store_name + " Day " + str(self.day) + " Transactions.csv"

        self.__makes_dirs()

        output_file_path = os.path.join(StoreSimulator.OUTPUT_DIR_NAME, self.store_name, output_file_name)

        # Make or overwrite the output file
        pd.DataFrame(self.customer_transactions, columns=["Transaction Id", "Customer Name", "Items", "Money Spent", "Time Entered", "Time Left"]).to_csv(output_file_path, index=False)

        del output_file_name
        del output_file_path
        
            

    def output_stock(self, title_ending_message: str = " After Day"):
        """
        Outputs item database to a directory specific to the store.
        """

        # Make the name of the file
        output_file_name = self.store_name + " Day " + str(self.day) + " Stock" + title_ending_message + ".csv"

        self.__makes_dirs()

        output_file_path = os.path.join(StoreSimulator.OUTPUT_DIR_NAME, self.store_name, output_file_name)

        # Make or overwrite the output file
        self.item_dataframe.to_csv(output_file_path, index=False)

        del output_file_name
        del output_file_path



    def add_stock(self, item_id: int, quantity: int = 20):
        """
        Adds the inputted quantity to the stock of the inputted item id.

        item_id: Id of the item which will have the stock change.

        quantity: Number to add to the item's stock.
        """

        # Get row index of item
        row_idex = self.get_row_index("Item Id", item_id)

        # Get current stock of item
        current_stock = self.item_dataframe.at[row_idex, "Stock"]
        
        # Add quantity to the item stock
        self.item_dataframe.at[row_idex, "Stock"] = round(current_stock + quantity)

        del current_stock



    def get_stock(self, item_id: int) -> int:
        """
        Returns stock of the inputted item id.
        """

        return self.item_dataframe.at[self.get_row_index("Item Id", item_id), "Stock"]



    def get_low_stock(self, stock_threshold: int = 10) -> pd.DataFrame:
        """
        Returns a dataframe of all items at or below the stock threshold.
        """

        return self.item_dataframe.loc[self.item_dataframe["Stock"] <= stock_threshold]
    


    def output_updated_stock(self):
        """
        Creates a specific csv file. Meant to be called after updating stock.
        """
        
        self.output_stock(" After Updating")



    def set_item_list(self, item_list_path: str):
        """
        Sets up fields related to the inputted item list.

        item_list_path: Path to the new item list. See "ItemList.csv" for an example of correct formatting.
        """

        self.item_dataframe = pd.read_csv(item_list_path)

        # Check if each item has a unique item id

        temp = set()

        for row in self.item_dataframe.iterrows():
            if row[1]["Item Id"] in temp:
                raise SyntaxError("Item Id '" + str(row[1]["Item Id"]) + "' occurs multiple times. Each Id must be unique.\n\nDuplicate Item Id Entry:\n\n" + str(row[1]))
            else:
                temp.add(row[1]["Item Id"])
        
        del temp
        
        # Translates the tags into a list

        temp = 0

        for row in self.item_dataframe["Tags"].copy():
            self.item_dataframe.at[temp, "Tags"] = literal_eval(row)
            temp = temp + 1

        # Set up data structures related to item list

        self.item_groups = {}
        self.item_group_names = []

        self.__init_item_groups()


    
    def check_if_name_in_store(self, name: str) -> bool:
        """
        Returns True if a customer is in the store and False otherwise.
        """

        return name in self.customers_in_store
    


    def get_income_for_current_day(self) -> float:
        """
        Returns the sum of all customer transactions for the current day.
        """
        
        total = 0

        for row in self.customer_transactions:
            total = total + float(row[3])

        return round(total, 2)
    


    def clear_store_directory(self):
        """
        Deletes all items in the store's directory in OUTPUT_DIR_NAME
        """

        files = glob.glob(StoreSimulator.OUTPUT_DIR_NAME + "/" + self.store_name + "/*.csv")
        for f in files:
            os.remove(f)
    


    def get_item(self, item_id: int) -> pd.DataFrame:
        """
        Returns an entry from the item dataframe of the inputted item id.
        """

        return self.item_dataframe.loc[self.item_dataframe["Item Id"] == item_id]
    


    def minutes_to_time(self, minutes: int) -> str:
        """
        Returns a string in the form of XX:XX to display time.
        """

        if int(minutes % 60) < 10:
            return str(int(minutes / 60)) + ":0" + str(int(minutes % 60))
        else:
            return str(int(minutes / 60)) + ":" + str(int(minutes % 60))
        

    
    def get_row_index(self, column_name: str, search_item) -> int:
        """
        Returns the row index of search_item in column_name.

        Does not work for any column that is a list-like structure.
        """

        return self.item_dataframe[self.item_dataframe[column_name] == search_item].index[0]
        

    
    def __makes_dirs(self):
        """
        Make directories for output files.
        """

        # Try to make or check for a directory for all outputs
        try:
            os.mkdir(StoreSimulator.OUTPUT_DIR_NAME)
        except FileExistsError:
            # Directory already exists
            pass

        # Try to make or check for a directory of the store
        try:
            os.mkdir(os.path.join(StoreSimulator.OUTPUT_DIR_NAME, self.store_name))
        except FileExistsError:
            # Directory already exists
            pass


    def __translate_items_bought(self, customer_dict: dict, include_item_name: bool = False) -> list:
        """
        Returns a list of all items a customer bought

        customer_dict: This is the items_bought field of a Customer object.

        include_item_name: Determines if the name of an item should be included in the list.
        """

        output = []
        name_column = self.item_dataframe.Name

        # Create a list of all items bought so all bought items can be stored in a single column

        if include_item_name:
            # Includes item name in the items column
            for key in customer_dict:
                output.append("Id:" + str(key) + " Name:" + name_column[key] + " Num:" + str(customer_dict[key]))
        else:
            # Only has id and quantity
            for key in customer_dict:
                output.append("Id:" + str(key) + " Num:" + str(customer_dict[key]))
        
        del name_column

        return output
    


    def __init_item_groups(self):
        """
        Initializes item_group related fields based on the item_dataframe.
        """

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
                    self.item_group_names.append(tag_str)



    def __get_customer_potential_buys(self, customer: cr.Customer) -> list:
        """
        Returns a list of lists where [0] is an item id and [1] is the item cost.
        """

        # Add every item in the input dataframe into a list
        output = []

        if "Any" in customer.item_tags:
            # Transverse the dataframe
            for row in self.item_dataframe.iterrows():
                if row[1]["Stock"] > 0:
                    for _ in range(0, row[1]["Weight"]):
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
                    for _ in range(0, row[1]["Weight"]):
                        output.append([row[1]["Item Id"], row[1]["Cost (USD)"]])

            del items
            del items_to_loc

        return output



# Test function for when this file is run

if __name__ == "__main__":
    print("Simulator Testing\n")
    
    test_sim = StoreSimulator("ItemList.csv",6.5,18,5,False,"Store Simulator")

    test_sim.simulate_one_day(use_random_customers=True)

    test_sim.output_stock()

    test_sim.output_transactions()

    test_sim.add_stock(1)
    test_sim.add_stock(2)
    test_sim.add_stock(3)

    test_sim.output_updated_stock()


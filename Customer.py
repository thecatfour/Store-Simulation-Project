
class Customer:



    def __init__(self, name: str = "Default Name", item_tags: list = ["Any"], money: float = 10.00, max_buy_attempts: float = 5.0, using_credit: bool = True):
        """
        Initializes a Customer object.

        name: Name of customer.

        item_tags: Tags that show what items that the customer wants to buy.

        money: Money the customer is willing to spend.

        max_buy_attempts: The max amount of items that a customer is willing to buy.

        using_credit: Allows a customer to spend more money than they brought.
        """

        self.name = name
        
        # Used to determine what customers will buy
        self.item_tags = item_tags
        
        self.starting_money = money
        self.money = money
        self.items_bought = {}

        # Used to determine the max amount of things the customer can buy
        self.max_buy_attempts = max_buy_attempts
        self.starting_buy_attempts = max_buy_attempts

        # Set by a store simulator object of when the customer entered the store (in minutes)
        self.enter = None

        # Used to determine if a customer's money count can go into the negatives
        self.using_credit = using_credit



    def buy_item(self, item_id: int, item_cost: float) -> bool:
        """
        Returns True if the customer bought the inputted item.

        item_id: Id of the item being bought.

        item_cost: Cost of the item being bought.
        """

        self.max_buy_attempts -= 1

        # Check if item can be bought
        if (item_cost <= self.money) or self.using_credit:
            self.money = self.money - item_cost

            # Check if customer already bought the item
            if item_id in self.items_bought:
                self.items_bought[item_id] += 1
            else:
                self.items_bought[item_id] = 1

            return True
        else:
            return False 
        


    def set_max_buy_attempts(self, new_max: float):
        """
        Sets the customer's max buy attempts to the input.
        """
        
        self.max_buy_attempts = round(new_max, 1)
        


    def set_money(self, new_money: float):
        """
        Sets the customer's money and starting money to the input. Should not be called while the customer is in a store.
        """

        self.money = round(new_money, 2)
        self.starting_money = self.money



    def reset_money_to_starting_money(self):
        """
        Sets the customer's money to their starting money.
        """

        self.money = self.starting_money



    def set_tags(self, new_tags: list):
        """
        Sets the customer's tags to the input.
        """

        del self.item_tags
        self.item_tags = new_tags
  


    def decrease_buy_attempts(self, lower_amount: float):
        """
        Decreases customer's max buy attempts by the input.
        """

        self.max_buy_attempts -= lower_amount



    def reset_items(self):
        """
        Resets customer's bought items. Should not be called while the customer is in a store.
        """

        del self.items_bought
        self.items_bought = {}



    def reset_customer(self):
        """
        Resets a customer to their initial state.
        """

        self.max_buy_attempts = self.starting_buy_attempts
        self.reset_items()
        self.reset_money_to_starting_money()
        self.set_enter(None)



    def get_money_difference(self) -> float:
        """
        Returns the difference between the customer's starting money and current money.
        """

        return self.starting_money - self.money
        


    def wants_more_items(self) -> bool:
        """
        Returns True if the customer is still willing to buy more items.
        """
        
        return self.max_buy_attempts > 0
    


    def set_enter(self, enter_time: int):
        """
        Sets the minutes of when the customer entered a store. This should only be set by a Store Simulator object.
        """
        
        self.enter = enter_time



    def __str__(self) -> str:
        """
        toString() for the customer.
        """

        return "Name: " + self.name + " ; Tags: " + ",".join(self.item_tags) + " ; Money: " + str(self.money) + " ; Bought: " + ",".join(self.items_bought) + " ; Remaining Buys: " + str(self.max_buy_attempts)
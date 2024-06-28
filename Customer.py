
class Customer:

    def __init__(self, name: str = "Default Name", item_tags: list = ["Any"], money: float = 10.00, max_buy_attempts: float = 5.0, using_credit: bool = True):
        self.name = name
        
        # Used to determine what customers will buy
        self.item_tags = item_tags
        
        self.starting_money = money
        self.money = money
        self.items_bought = {}

        # Used to determine the max amount of things the customer can buy
        self.max_buy_attempts = max_buy_attempts

        # Set by a store simulator object of when the customer entered the store (in minutes)
        self.enter = None

        # Used to determine if a customer's money count can go into the negatives
        self.using_credit = using_credit

    def buy_item(self, item_id: int, item_cost: float) -> bool:
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
  
    def decrease_buy_attempts(self, lower_amount: float):
        self.max_buy_attempts -= lower_amount

    def reset_items(self):
        del self.items_bought
        self.items_bought = {}

    def get_money_difference(self) -> float:
        return self.starting_money - self.money
        
    def wants_more_items(self) -> bool:
        return self.max_buy_attempts > 0
    
    def set_enter(self, enter_time: int):
        self.enter = enter_time

    def __str__(self) -> str:
        return "Name:" + self.name + " -- Tags:" + ",".join(self.item_tags) + " -- Money:" + str(self.money) + " -- Bought:" + ",".join(self.items_bought)
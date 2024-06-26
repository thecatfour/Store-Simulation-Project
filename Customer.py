
class Customer:

    def __init__(self, name: str = "Default Name", item_tags: list = [], money: float = 10.00, max_buy_attempts: float = 5.0):
        self.name = name
        self.item_tags = item_tags
        self.starting_money = money
        self.money = money
        self.items_bought = {}
        self.max_buy_attempts = max_buy_attempts
        self.enter = None

    def buy_item(self, item_id: int, item_cost: float) -> bool:
        self.max_buy_attempts -= 1

        # Check if item can be bought
        if item_cost <= self.money:
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

class Customer:

    def __init__(self, name: str = "Default Name", item_tags: list = [], money: float = 10.00, max_items: int = 5):
        self.name = name
        self.item_tags = item_tags
        self.money = money
        self.items_bought = {}
        self.max_items = max_items

    def buy_item(self, item_id: int, item_cost: float) -> bool:
        # Check if item can be bought
        if item_cost <= self.money:
            self.money = self.money - item_cost

            # Check if customer already bought the item
            if item_id in self.items_bought:
                self.items_bought[item_id] += 1
            else:
                self.items_bought[item_id] = 1
            
            self.max_items -= 1

            return True
        else:
            
            return False
        
    def wants_more_items(self) -> bool:
        return self.max_items > 0
    
    def set_name(self, new_name: str):
        self.name = new_name

    def __str__(self) -> str:
        return "Name:" + self.name + " -- Tags:" + ",".join(self.item_tags) + " -- Money:" + str(self.money) + " -- Bought:" + ",".join(self.items_bought)
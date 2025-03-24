def calculate_total(orders):
    sum = 0
    for i in orders:
        sum += i["value"]
    return sum

def process_order(order):
    """Process a single order"""
    return order["value"] * 1.1  # Adding 10% tax

class OrderProcessor:
    def __init__(self):
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)
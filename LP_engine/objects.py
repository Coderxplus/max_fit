class Product:
    def __init__(self, name, profit, usage):
        self.name = name
        self.profit = profit
        self.usage = usage   # dict of constraint usage e.g {"Time": 3, "Labour": 4} # list of Constraints objects

    def __str__(self):
        # Display constraints nicely
        return f"name: {self.name}\nprofit: {self.profit}\nconstraints: [{self.usage}]"

    def to_dict(self):
        # Convert product to dictionary, including constraints as dicts
        return {
            "name": self.name,
            "profit": self.profit,
            "usage": self.usage
        }


class Constraint:
    def __init__(self, name, max_value):
        self.name = name
        self.max_value = max_value
    
    def __str__(self):
        return f"name: {self.name}, value: {self.max_value}"

    def to_dict(self):
        return {
            "name": self.name,
            "max_value": self.max_value
        }



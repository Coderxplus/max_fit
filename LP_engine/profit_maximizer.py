from objects import Product, Constraint
import pulp


class ProfitOptimizer:
    def __init__(self, no_of_products=None, no_of_constraints=None):
        self.no_of_products = no_of_products
        self.no_of_constraints = no_of_constraints
        self.products = []
        self.constraints_list = []

    def collect_counts(self):
        if self.no_of_products is None:
            self.no_of_products = int(input("Enter number of products: "))
        if self.no_of_constraints is None:
            self.no_of_constraints = int(input("Enter number of constraints: "))

    def collect_constraints(self):
        for _ in range(self.no_of_constraints):
            print("Enter system-wide constraints:")
            name = input("Enter constraint name (e.g. Time, Labour): ")
            max_val = float(input("Enter max allowed value of this constraint: "))
            self.constraints_list.append(Constraint(name, max_val))

    def collect_products(self):
        for _ in range(self.no_of_products):
            print("-----------------------------------------------------------------")
            name = input("Enter name of product: ")
            profit = float(input("Enter profit per unit ($): "))

            usage = {}
            for constraint in self.constraints_list:
                val = float(input(f"Enter usage of '{constraint.name}' for product '{name}': "))
                usage[constraint.name] = val

            product = Product(name, profit, usage=usage)
            self.products.append(product)

    def solve_lp(self):
        """Build and solve the LP model."""


        model = pulp.LpProblem("Product_Mix_Optimization", pulp.LpMaximize)


        qty_vars = {p.name: pulp.LpVariable(p.name, lowBound=0, cat="Continuous")
                    for p in self.products}


        model += pulp.lpSum(qty_vars[p.name] * p.profit for p in self.products)

        for constraint in self.constraints_list:
            model += pulp.lpSum(
                qty_vars[p.name] * p.usage[constraint.name]
                for p in self.products
            ) <= constraint.max_value, constraint.name

        model.solve()

        print("\n===== OPTIMAL SOLUTION =====")
        print(f"Status: {pulp.LpStatus[model.status]}\n")

        for p in self.products:
            print(f"{p.name}: {qty_vars[p.name].varValue}")

        print("\nTotal Profit:", pulp.value(model.objective))

    def run(self):
        self.collect_counts()
        self.collect_constraints()
        self.collect_products()
        self.solve_lp()   

    def output(self):
        for product in self.products:
            print(product.to_dict())


if __name__ == "__main__":
    app = ProfitOptimizer()
    app.run()
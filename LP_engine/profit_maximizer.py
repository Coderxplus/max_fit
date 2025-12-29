from objects import Product, Constraint
import pulp
import pandas as pd

class ProfitOptimizer:
    def __init__(self, no_of_products=None, no_of_constraints=None, csv_file=None):
        self.csv_file = csv_file
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

    def load_from_csv(self):
        if not self.csv_file:
            raise ValueError("No CSV file provided.")

        df = pd.read_csv(self.csv_file)

        data = df[df["product_id"] != "LIMITS"]
        limits_row = df[df["product_id"] == "LIMITS"].squeeze()

        data["unit_profit"] = data["unit_profit"].astype(float)
        usage_columns = df.columns[3:]
        data[usage_columns] = data[usage_columns].astype(float)

        self.constraints_list = [
            Constraint(name=col, max_value=float(limits_row[col]))
            for col in usage_columns
        ]

        for _, row in data.iterrows():
            usage = {col: row[col] for col in usage_columns}
            product = Product(name=row["product_name"], profit=row["unit_profit"], usage=usage)
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
        # self.collect_counts()
        # self.collect_constraints()
        # self.collect_products()
        self.csv_file="LP_engine\csv_file\hybrid_manufacturing_cleaned.csv"
        self.load_from_csv()
        self.solve_lp()   

    def output(self):
        for product in self.products:
            print(product.to_dict())


if __name__ == "__main__":
    app = ProfitOptimizer()
    app.run()
import pulp
import pandas as pd


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




class ProfitOptimizer:
    def __init__(self, no_of_products=None, no_of_constraints=None, csv_file=None,):
        self.csv_file = csv_file
        self.no_of_products = no_of_products
        self.no_of_constraints = no_of_constraints
        self.products = []
        self.constraints_list = []
        

    def collect_constraints(self, name, max_val):
        self.constraints_list.append(Constraint(name, max_val))

    def collect_products(self, name, profit, usage):
            product = Product(name, profit, usage=usage)
            self.products.append(product)

    def load_csv(self):
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
            product = Product(name=row["product_id"], profit=row["unit_profit"], usage=usage)
            self.products.append(product)

    def solve_lp(self):
        """Build and solve the LP model and return results."""
        
        model = pulp.LpProblem("Product_Mix_Optimization", pulp.LpMaximize)

        # Create variables
        qty_vars = {p.name: pulp.LpVariable(p.name, lowBound=0, cat="Continuous")
                    for p in self.products}

        # Objective function
        model += pulp.lpSum(qty_vars[p.name] * p.profit for p in self.products)

        # Constraints
        for constraint in self.constraints_list:
            model += pulp.lpSum(
                qty_vars[p.name] * p.usage[constraint.name]
                for p in self.products
            ) <= constraint.max_value, constraint.name

        # Solve the model
        model.solve()

        # Total profit
        total_profit = pulp.value(model.objective)

        # Collect results
        results = {
            "total_profit": total_profit,
            "quantities": [],
            "resource_usage": []
        }

        # Non-zero quantities
        for p in self.products:
            qty = qty_vars[p.name].varValue
            if qty and qty > 0:
                results["quantities"].append({
                    "product_name": p.name,
                    "quantity": qty,
                    "profit": p.profit,
                    "total_product_profit": qty * p.profit
                })
        
        # Resource usage summary
        for constraint in self.constraints_list:
            used = sum(qty_vars[p.name].varValue * p.usage[constraint.name] for p in self.products)
            percent = (used / constraint.max_value) * 100 if constraint.max_value != 0 else 0
            results["resource_usage"].append({
                "constraint_name": constraint.name,
                "used": used,
                "limit": constraint.max_value,
                "percent": percent
            })

        return results
def solve_lp(self):
    """Build and solve the LP model and return results."""
    
    model = pulp.LpProblem("Product_Mix_Optimization", pulp.LpMaximize)

    # Create variables
    qty_vars = {
        p.name: pulp.LpVariable(p.name, lowBound=0, cat="Continuous")
        for p in self.products
    }

    # Objective function
    model += pulp.lpSum(
        qty_vars[p.name] * p.profit
        for p in self.products
    )

    # Constraints
    for constraint in self.constraints_list:
        model += (
            pulp.lpSum(
                qty_vars[p.name] * p.usage.get(constraint.name, 0)
                for p in self.products
            )
            <= constraint.max_value,
            constraint.name
        )

    # Solve
    model.solve()

    total_profit = pulp.value(model.objective)

    results = {
        "total_profit": total_profit,
        "quantities": [],
        "resource_usage": []
    }

    # Non-zero quantities
    for p in self.products:
        qty = qty_vars[p.name].varValue
        if qty and qty > 0:
            results["quantities"].append({
                "product_name": p.name,
                "quantity": qty,
                "profit": p.profit,
                "total_product_profit": qty * p.profit
            })

    # Resource usage summary
    for constraint in self.constraints_list:
        used = sum(
            qty_vars[p.name].varValue * p.usage.get(constraint.name, 0)
            for p in self.products
            if qty_vars[p.name].varValue is not None
        )

        percent = (
            (used / constraint.max_value) * 100
            if constraint.max_value != 0
            else 0
        )

        results["resource_usage"].append({
            "constraint_name": constraint.name,
            "used": used,
            "limit": constraint.max_value,
            "percent": percent
        })

    return results

    def run(self):
        # self.collect_counts()
        # self.collect_constraints()
        # self.collect_products()
        # self.csv_file="LP_engine\csv_file\hybrid_manufacturing_cleaned.csv"
        # self.load_from_csv()
        self.solve_lp()   
        self.output()

    def output(self):
        for product in self.products:
            print(product.to_dict())


if __name__ == "__main__":
    app = ProfitOptimizer()
    app.run()
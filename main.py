from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped , mapped_column
from flask_migrate import Migrate
from LP_engine.profit_maximizer import ProfitOptimizer
from werkzeug.utils import secure_filename
import os


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()


UPLOAD_FOLDER = 'uploads'

ALLOWED_EXTENSIONS = {'csv'}
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

db.init_app(app)
migrate.init_app(app, db)

class Product(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    profit: Mapped[float] = mapped_column()
    unit: Mapped[str] = mapped_column()
    max_quantity: Mapped[float] = mapped_column()
    min_quantity: Mapped[float] = mapped_column()
    

class Constraint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    max_value: Mapped[float] = mapped_column()


class Results(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity_name: Mapped[str] = mapped_column()
    quantity_value: Mapped[float] = mapped_column()
    optimized_profit: Mapped[float] = mapped_column()
    usage_name: Mapped[str] = mapped_column()
    usage_value: Mapped[float] = mapped_column()
    usage_limit: Mapped[float]= mapped_column()
    usage_percent: Mapped[float] = mapped_column()

    max_value: Mapped[float] = mapped_column()
"""
    product_id (FK)
    constraint_id (FK)
    usage_value
"""


class ProductConstraint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(db.ForeignKey("product.id")) 
    constraint_id: Mapped[int] = mapped_column(db.ForeignKey("constraint.id"))
    usage_value: Mapped[float] = mapped_column()
    # Eagerly expose linked product/constraint for templates
    product = db.relationship("Product", backref="product_constraints")
    constraint = db.relationship("Constraint", backref="product_constraints")

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/view_csv")
def view_csv():
    return render_template("csv.html")


# Product end points
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    products = Product.query.all()
    name = request.form["name"]
    profit = request.form["profit"]
    unit = request.form["unit"]
    min_quantity = request.form["min_quantity"]
    max_quantity = request.form["max_quantity"]
    product = Product(name=name, profit=profit, unit=unit, min_quantity=min_quantity, max_quantity=max_quantity)
    db.session.add(product)
    db.session.commit()
    return redirect(url_for("get_products"))

@app.route("/delete_product/<response>", methods=["GET", "POST"])
def delete_product(response):
    product = Product.query.filter_by(id=response).first_or_404()
    
    # Delete all product constraints associated with this product
    ProductConstraint.query.filter_by(product_id=response).delete()
    
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("get_products"))

@app.route("/products", methods=["GET", "POST"])
def get_products():
    products = Product.query.all()
    return render_template("products.html", products=products)

@app.route("/constraints", methods=["GET", "POST"])
def get_constraints():
    constraints = Constraint.query.all()
    return render_template("constraints.html", constraints=constraints)

@app.route("/usages", methods=["GET"])
def get_usages():
    products = Product.query.all()
    constraints = Constraint.query.all()
    usages = ProductConstraint.query.all()
    return render_template(
        "assignments.html",
        products=products,
        constraints=constraints,
        usages=usages
    )

# Dashboard page
@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


#Constraint Endpoints
@app.route("/api/constraints", methods=["POST"])
def add_constraints():
    name = request.form["name"]
    max_value = request.form["max_value"]
    constraint = Constraint(name=name, max_value=max_value)
    db.session.add(constraint)
    db.session.commit()
    return redirect(url_for("get_constraints"))

@app.route("/api/constraints/<int:constraint_id>", methods=["POST"])
def delete_constraints(constraint_id):
    constraint = Constraint.query.filter_by(id=constraint_id).first_or_404()
    
    # Delete all product constraints associated with this constraint
    ProductConstraint.query.filter_by(constraint_id=constraint_id).delete()
    
    db.session.delete(constraint)
    db.session.commit()
    return redirect(url_for("get_constraints"))


#Usage Endpoints
@app.route("/api/product-constraints", methods=["POST"])
def add_usages():
    product_id = request.form["product_id"]
    constraints_data = request.form.to_dict(flat=False)
    for key in constraints_data:
        if key.startswith('constraints[') and key.endswith('][usage_value]'):
            constraint_id = key.split('[')[1].split(']')[0]
            usage_value = request.form.get(key)
            
            if usage_value and float(usage_value) > 0:
                product_constraint = ProductConstraint(
                    product_id=product_id,
                    constraint_id=constraint_id,
                    usage_value=float(usage_value)
                )
                db.session.add(product_constraint)
    
    db.session.commit()
    return redirect(url_for("get_usages"))

@app.route("/delete_usages/<int:response>", methods=["POST"])
def delete_usages(response):
    data = ProductConstraint.query.filter_by(id=response).first_or_404()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("get_usages"))

@app.route("/upload_csv/", methods=["POST"])
def upload_csv_file():
    optimizer = ProfitOptimizer()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            optimizer.csv_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            optimizer.load_csv()
            results = optimizer.solve_lp()
            # Clear previous results
            Results.query.delete()  
            # Save results to database
            if results:
                # Store product quantities
                for qty_data in results["quantities"]:
                    result = Results(
                        quantity_name=qty_data["product_name"],
                        quantity_value=qty_data["quantity"],
                        optimized_profit=results["total_profit"],
                        usage_name="",
                        usage_value=0,
                        usage_limit=0,
                        usage_percent=0,
                        max_value=qty_data["total_product_profit"]
                    )
                    db.session.add(result)
                
                # Store resource usage
                for usage_data in results["resource_usage"]:
                    result = Results(
                        quantity_name="",
                        quantity_value=0,
                        optimized_profit=results["total_profit"],
                        usage_name=usage_data["constraint_name"],
                        usage_value=usage_data["used"],
                        usage_limit=usage_data["limit"],
                        usage_percent=usage_data["percent"],
                        max_value=0
                    )
                    db.session.add(result)
                
                db.session.commit()
            
            return redirect(url_for('get_result', name=filename))
    return render_template("CSV.html")

def optimize():
    optimizer = ProfitOptimizer()
    
    # Collect all constraints from database
    constraints = Constraint.query.all()
    for constraint in constraints:
        optimizer.collect_constraints(name=constraint.name, max_val=constraint.max_value)
    
    # Collect all products with their constraint usage values
    products = Product.query.all()
    for product in products:
        usages = ProductConstraint.query.filter_by(product_id=product.id).all()
        usage_dict = {}
        for usage in usages:
            constraint = Constraint.query.get(usage.constraint_id)
            usage_dict[constraint.name] = usage.usage_value
        
        optimizer.collect_products(name=product.name, profit=product.profit, usage=usage_dict)
    
    # Solve the optimization problem and get results
    results = optimizer.solve_lp()
    
    # Clear previous results
    Results.query.delete()
    
    # Save results to database
    if results:
        # Store product quantities
        for qty_data in results["quantities"]:
            result = Results(
                quantity_name=qty_data["product_name"],
                quantity_value=qty_data["quantity"],
                optimized_profit=results["total_profit"],
                usage_name="",
                usage_value=0,
                usage_limit=0,
                usage_percent=0,
                max_value=qty_data["total_product_profit"]
            )
            db.session.add(result)
        
        # Store resource usage
        for usage_data in results["resource_usage"]:
            result = Results(
                quantity_name="",
                quantity_value=0,
                optimized_profit=results["total_profit"],
                usage_name=usage_data["constraint_name"],
                usage_value=usage_data["used"],
                usage_limit=usage_data["limit"],
                usage_percent=usage_data["percent"],
                max_value=0
            )
            db.session.add(result)
        
        db.session.commit()
    
    return results

@app.route("/api/optimize", methods=["POST"])
def run_optimization():
    optimize()
    return redirect(url_for("get_result"))

@app.route("/results", methods=["GET"]) 
def get_result():
    redirect(url_for("run_optimization"))
    results = Results.query.all()
    return render_template("dashboard.html", results=results)

@app.route("/download_results", methods=["GET"]) 
def download_results():
    pass

if __name__ == "__main__":
    app.run(debug=True)
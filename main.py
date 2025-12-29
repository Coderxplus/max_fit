from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped , mapped_column


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

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

"""product_id (FK)
constraint_id (FK)
usage_value

"""


class ProductConstraint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id:Mapped[int] = mapped_column(foreign_key="product.id") 
    constraint_id:Mapped[int] = mapped_column(foreign_key="constraint.id")

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    name = request.form["name"]
    profit = request.form["profit"]
    unit = request.form["unit"]
    min_quantity = request.form["min_quantity"]
    max_quantity = request.form["max_qunatity"]
    product = Product(name=name, profit=profit, unit=unit, min_quantity=min_quantity, max_quantity=max_quantity)
    db.session.add(product)
    db.session.commit()

@app.route("/delete_product/<response>", methods=["GET", "POST"])
def delete(response):
    data = Product.query.filter_by(id=response).first_or_404()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
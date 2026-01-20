# Maxfit - Profit Optimization System

A Flask-based web application that optimizes product mix to maximize profit using linear programming. Maxfit helps manufacturers determine the optimal quantity of each product to produce given resource constraints.

## Features

- **Product Management**: Add, edit, and manage products with profit information
- **Constraint Management**: Define resource constraints (time, labor, materials, etc.)
- **Product-Constraint Assignments**: Assign resource usage values for each product
- **Optimization Engine**: Uses linear programming (PuLP) to solve the product mix optimization problem
- **CSV Import**: Upload and process CSV files with product and constraint data
- **Dashboard**: Visual display of optimization results with resource utilization charts
- **Download Results**: Export optimization results as CSV files

## Technologies

- **Backend**: Flask, SQLAlchemy, Flask-Migrate
- **Optimization**: PuLP (Linear Programming solver)
- **Data Processing**: Pandas
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Icons**: Font Awesome 6.5.1

## Project Structure

```
Maxfit/
├── main.py                           # Flask app entry point
├── LP_engine/
│   ├── profit_maximizer.py          # Linear programming optimization logic
│   └── csv_file/
│       └── hybrid_manufacturing_cleaned.csv
├── templates/
│   ├── index.html                   # Home page
│   ├── dashboard.html               # Optimization results & visualization
│   ├── products.html                # Product management
│   ├── constraints.html             # Constraint management
│   ├── assignments.html             # Product-constraint assignments
│   └── CSV.html                     # CSV upload interface
├── static/
│   └── styles.css                   # Global stylesheet
├── uploads/                         # Uploaded files & optimization results
├── migrations/                      # Database migration files (Alembic)
├── instance/                        # Instance-specific files
└── package.json                     # Project metadata

```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd c:\Users\user\projects\Maxfit
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install flask flask-sqlalchemy flask-migrate pulp pandas werkzeug
   ```

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

## Running the Application

1. **Start the Flask development server:**
   ```bash
   python main.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Usage

### 1. Set Up Products
- Navigate to **Products** page
- Click "Add Product" to create new products
- Enter product name, profit per unit, unit type, and quantity limits

### 2. Define Constraints
- Navigate to **Constraints** page
- Add resource constraints (e.g., "Machine Time: 100 hours", "Labour: 50 hours")
- Set maximum available value for each constraint

### 3. Assign Product Usage
- Navigate to **Product-Constraints** page
- Assign how much of each resource each product uses
- Example: Product A uses 2 hours of Machine Time and 1 hour of Labour

### 4. Run Optimization
- Go to **Dashboard**
- Click "Run Optimization" button
- View the optimal product quantities and resource utilization

### 5. Download Results
- After optimization, click "Download Results as CSV"
- Results include optimal quantities, profits, and resource usage percentages

### 6. Upload CSV File
- Navigate to **CSV** page
- Upload a pre-formatted CSV with product and constraint data
- System auto-runs optimization and displays results

## CSV Format

The CSV file should contain products as rows and constraints as columns:

```
product_id,product_name,unit_profit,constraint1,constraint2,...
PRODUCT_A,Product A,100,2,1
PRODUCT_B,Product B,150,3,2
LIMITS,,,80,50
```

Last row must be "LIMITS" with maximum available values for each constraint.

## API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Home page |
| `/dashboard` | GET | Optimization dashboard |
| `/products` | GET | View products |
| `/add_product` | POST | Add new product |
| `/delete_product/<id>` | POST | Delete product |
| `/constraints` | GET | View constraints |
| `/api/constraints` | POST | Add constraint |
| `/api/constraints/<id>` | POST | Delete constraint |
| `/usages` | GET | View product-constraint assignments |
| `/api/product-constraints` | POST | Add assignment |
| `/delete_usages/<id>` | POST | Delete assignment |
| `/api/optimize` | POST | Run optimization |
| `/upload_csv` | POST | Upload and process CSV file |
| `/download_results` | GET | Download optimization results as CSV |

## Optimization Algorithm

The system uses **Linear Programming (LP)** via PuLP to solve:

```
Maximize: Σ(profit_i × quantity_i)

Subject to:
  Σ(usage_constraint_j × quantity_i) ≤ limit_j  ∀ constraints
  quantity_i ≥ 0  ∀ products
```

This determines the optimal product mix that maximizes total profit while respecting all resource constraints.

## Output CSV Structure

The downloaded CSV contains:
- **Product Quantities Section**: Optimal quantity to produce for each product with individual profit contributions
- **Resource Usage Section**: Actual usage vs. limit for each constraint with utilization percentage

## Troubleshooting

**No results showing after optimization:**
- Ensure all products have constraint assignments
- Check that constraint limits are set correctly
- Verify CSV data is properly formatted

**Database errors:**
- Delete `project.db` and re-run the app to reset database
- Run `flask db upgrade` to apply migrations

**Optimization returns zero quantities:**
- Check that products have positive profit values
- Verify constraint assignments exist for all products
- Ensure constraint limits are not too restrictive

## Future Enhancements

- Support for integer programming (whole unit quantities)
- Sensitivity analysis
- Multi-period optimization
- Advanced constraint types (min/max product quantities)
- Batch optimization runs
- User authentication

## License

Private Project

## Support

For issues or questions, refer to the Flask and PuLP documentation:
- Flask: https://flask.palletsprojects.com/
- PuLP: https://coin-or.github.io/pulp/
- SQLAlchemy: https://www.sqlalchemy.org/

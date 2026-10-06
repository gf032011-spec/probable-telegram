import os
from datetime import datetime, timezone
from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# --- APPLICATION SETUP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zemene-gebeya-super-secret-key-112233')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- DATABASE MODELS ---

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    role = db.Column(db.String(20), nullable=False, default='Customer')
    
    businesses = db.relationship('Business', backref='registrar', lazy=True, cascade="all, delete-orphan")
    orders = db.relationship('Order', backref='buyer', lazy=True, cascade="all, delete-orphan")

class Business(db.Model):
    __tablename__ = 'Businesses'
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False)
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(150), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    registration_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    
    products = db.relationship('Product', backref='associated_shop', lazy=True, cascade="all, delete-orphan")

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    cost_buy = db.Column(db.Float, nullable=False, default=0.0)
    cost_sell = db.Column(db.Float, nullable=False, default=0.0)
    image_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    business_id = db.Column(db.Integer, db.ForeignKey('Businesses.id'), nullable=False)
    
    order_items = db.relationship('Order', backref='product_profile', lazy=True, cascade="all, delete-orphan")

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'), nullable=False)
    quantity_bought = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- BASE HTML TEMPLATE ---

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zemene Gebeya - Trade Platform</title>
    <style>
        body { background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; color: #1e293b; }
        .navbar { background: #0f172a; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .navbar h2 { margin: 0; font-size: 1.4rem; font-weight: 800; color: #38bdf8; letter-spacing: -0.5px; }
        .nav-links { display: flex; align-items: center; gap: 20px; }
        .nav-links a { color: #94a3b8; text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: color 0.2s; }
        .nav-links a:hover { color: white; }
        .role-badge { padding: 3px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; background: #38bdf8; color: #0f172a; }
        .main-container { max-width: 1250px; margin: 40px auto; padding: 0 20px; box-sizing: border-box; }
        .card { background: #ffffff; padding: 25px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; width: 100%; box-sizing: border-box; margin-bottom: 30px; }
        .text-center { text-align: center; }
        .form-group { margin-bottom: 1.25rem; text-align: left; }
        .form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem; color: #475569; }
        .form-control, .form-select { display: block; width: 100%; padding: 0.65rem 0.75rem; font-size: 0.95rem; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; background-color: #f8fafc; }
        .btn { display: inline-block; font-weight: 700; text-align: center; cursor: pointer; padding: 0.7rem 1.5rem; font-size: 0.95rem; border-radius: 8px; border: 1px solid transparent; text-decoration: none; box-sizing: border-box; width: 100%; transition: all 0.2s; }
        .btn-primary { color: #ffffff; background-color: #0284c7; }
        .btn-success { color: #ffffff; background-color: #16a34a; }
        .btn-danger { color: #ffffff; background-color: #dc2626; }
        .btn-sm { padding: 0.4rem 0.8rem; font-size: 0.8rem; border-radius: 6px; width: auto; }
        .alert { padding: 1rem 1.25rem; margin-bottom: 1.5rem; border-radius: 8px; font-weight: 500; font-size: 0.95rem; }
        .alert-danger { color: #991b1b; background-color: #fee2e2; border: 1px solid #fca5a5; }
        .alert-success { color: #166534; background-color: #dcfce7; border: 1px solid #86efac; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 25px; margin-bottom: 30px; }
        .stats-grid .stat-box { background: white; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }
        .stats-grid .stat-box h3 { margin: 0 0 5px 0; font-size: 2.2rem; color: #0284c7; font-weight: 800; }
        .stats-grid .stat-box p { margin: 0; color: #64748b; font-weight: 600; font-size: 0.95rem; }
        .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 30px; margin-top: 20px; }
        .product-card { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); display: flex; flex-direction: column; transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-4px); }
        .product-img { width: 100%; height: 180px; object-fit: cover; background: #e2e8f0; display: flex; align-items: center; justify-content: center; font-size: 3rem; color: #94a3b8; }
        .product-info { padding: 20px; flex-grow: 1; display: flex; flex-direction: column; }
        .product-title { margin: 0 0 8px 0; font-size: 1.15rem; font-weight: 700; color: #0f172a; }
        .product-meta { font-size: 0.85rem; color: #64748b; margin-bottom: 6px; }
        .product-price { font-size: 1.3rem; font-weight: 800; color: #16a34a; margin: 12px 0; }
        table { width: 100%; border-collapse: collapse; background: #ffffff; margin-top: 10px; border-radius: 10px; overflow: hidden; }
        th, td { padding: 1rem; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }
        th { background-color: #f1f5f9; font-weight: 700; color: #475569; }
        .table-responsive { width: 100%; overflow-x: auto; border: 1px solid #e2e8f0; border-radius: 10px; background: white; }
    </style>
</head>
<body>
    <div class="navbar">
        <h2>Zemene Gebeya ዘመነ ገበያ</h2>
        <div class="nav-links">
            {% if current_user.is_authenticated %}
                <span>User: <strong>{{ current_user.username }}</strong> <span class="role-badge">{{ current_user.role }}</span></span>
                <a href="{{ url_for('dashboard') }}">Dashboard Workspace</a>
                <a href="{{ url_for('logout') }}">Logout</a>
            {% else %}
                <a href="{{ url_for('login') }}">Login Portal</a>
                <a href="{{ url_for('register') }}">Register Portal</a>
            {% endif %}
        </div>
    </div>
    <div class="main-container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category=='error' else 'success' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception:
            flash('Database authentication error. Please try again.', 'error')
            
    return render_template_string(BASE_LAYOUT + """
    <div style="display: flex; justify-content: center; align-items: center; min-height: 70vh;">
        <div class="card" style="max-width: 420px;">
            <h3 class="text-center" style="margin-top:0;font-weight:800;font-size:1.5rem;color:#0f172a;">Account Login</h3>
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Enter password">
                </div>
                <button type="submit" class="btn btn-primary" style="width:100%; margin-top:10px;">Login</button>
            </form>
            <div class="text-center" style="margin-top: 20px; font-size:0.9rem; color:#64748b;">
                New to the market? <a href="/register" style="color:#0284c7;text-decoration:none;font-weight:700;">Create Account</a>
            </div>
        </div>
    </div>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'Customer')
        try:
            existing_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
            if existing_user:
                flash('Username already registered in system matrix!', 'error')
            else:
                new_user = User(username=username, password=generate_password_hash(password), role=role)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! Please sign in.', 'success')
                return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            flash('Registration terminal routing error.', 'error')
            
    return render_template_string(BASE_LAYOUT + """
    <div style="display: flex; justify-content: center; align-items: center; min-height: 70vh;">
        <div class="card" style="max-width: 420px;">
            <h3 class="text-center" style="margin-top:0;font-weight:800;font-size:1.5rem;color:#0f172a;">Create Market Account</h3>
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required placeholder="Create username">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Create password">
                </div>
                <div class="form-group">
                    <label class="form-label">Account Profile Type</label>
                    <select name="role" class="form-select">
                        <option value="Customer">Standard Customer (Buy Products)</option>
                        <option value="Merchant">Merchant Businessman (Register Products)</option>
                        <option value="Admin">System Administrator (Edit & Update All)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success" style="width:100%; margin-top:10px;">Sign Up</button>
            </form>
            <div class="text-center" style="margin-top: 20px; font-size:0.9rem;">
                <a href="/login" style="color:#0284c7;text-decoration:none;font-weight:700;">Back to Login</a>
            </div>
        </div>
    </div>
    """)

@app.route('/dashboard')
def dashboard():
    search_q = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    total_users = db.session.scalar(db.select(db.func.count(User.id))) or 0
    total_products = db.session.scalar(db.select(db.func.count(Product.id))) or 0
    total_orders = db.session.scalar(db.select(db.func.count(Order.id))) or 0

    p_stmt = db.select(Product)
    if search_q:
        p_stmt = p_stmt.filter(Product.product_name.contains(search_q))
    if category_filter:
        p_stmt = p_stmt.filter_by(category=category_filter)
    
    product_list = db.session.scalars(p_stmt).all()
    business_list = db.session.scalars(db.select(Business)).all()
    user_list = db.session.scalars(db.select(User)).all()
    all_orders = db.session.scalars(db.select(Order)).all()

    # Safe boolean checks passed directly into template
    is_authenticated = current_user.is_authenticated
    is_admin = is_authenticated and getattr(current_user, 'role', None) == 'Admin'
    is_merchant_or_admin = is_authenticated and getattr(current_user, 'role', None) in ['Merchant', 'Admin']

    if is_authenticated:
        if is_admin:
            my_businesses = business_list
        else:
            my_businesses = db.session.scalars(db.select(Business).filter_by(user_id=current_user.id)).all()
    else:
        my_businesses = []

    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="stats-grid">
        <div class="stat-box">
            <h3>{{ total_products }}</h3>
            <p>Total Products on Display</p>
        </div>
        <div class="stat-box">
            <h3>{{ total_orders }}</h3>
            <p>Successful Transactions Executed</p>
        </div>
        <div class="stat-box">
            <h3>{{ total_users }}</h3>
            <p>Active Registered Market Entities</p>
        </div>
    </div>
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #e2e8f0; padding-bottom:12px; margin-bottom:20px; flex-wrap:wrap; gap:10px;">
            <h3 style="margin:0; font-weight:800; color:#0f172a;">Zemene Gebeya Market Showcase</h3>
            <p style="margin:0; color:#64748b; font-weight:600;">Interactive visual stock listings directory</p>
        </div>
        <form method="GET" action="{{ url_for('dashboard') }}" style="display:flex; gap:15px; margin-bottom:25px; align-items:flex-end; flex-wrap:wrap;">
            <div style="flex:2; min-width:240px;">
                <label class="form-label">Look Up Product</label>
                <input type="text" name="search" class="form-control" value="{{ search_q }}" placeholder="Search products by name...">
            </div>
            <div style="flex:1; min-width:180px;">
                <label class="form-label">Category Filter</label>
                <select name="category" class="form-select">
                    <option value="">All Categories</option>
                    <option value="Electronics" {% if category_filter == 'Electronics' %}selected{% endif %}>Electronics</option>
                    <option value="Clothing & Fashion" {% if category_filter == 'Clothing & Fashion' %}selected{% endif %}>Clothing & Fashion</option>
                    <option value="Agriculture & Food" {% if category_filter == 'Agriculture & Food' %}selected{% endif %}>Agriculture & Food</option>
                    <option value="Cosmetics & Beauty" {% if category_filter == 'Cosmetics & Beauty' %}selected{% endif %}>Cosmetics & Beauty</option>
                    <option value="Home & Construction" {% if category_filter == 'Home & Construction' %}selected{% endif %}>Home & Construction</option>
                </select>
            </div>
            <div style="display:flex; gap:10px;">
                <button type="submit" class="btn btn-primary" style="padding:0.65rem 1.5rem;">Search</button>
                <a href="{{ url_for('dashboard') }}" class="btn btn-danger" style="padding:0.65rem 1rem; background-color:#64748b;">Reset</a>
            </div>
        </form>
        <div class="product-grid">
            {% for p in product_list %}
            <div class="product-card">
                <div class="product-img">&#128230;</div>
                <div class="product-info">
                    <span style="font-size:0.75rem; text-transform:uppercase; font-weight:bold; letter-spacing:0.5px; color:#0284c7;">{{ p.category }}</span>
                    <h4 class="product-title">{{ p.product_name }}</h4>
                    <div class="product-meta">Shop Vendor: <strong>{{ p.associated_shop.business_name if p.associated_shop else 'N/A' }}</strong></div>
                    <div class="product-meta">Total Stock Available: <strong style="color:#0f172a;">{{ p.quantity }} units</strong></div>
                    {% if is_admin %}
                        <div style="background:#f1f5f9; padding:8px; border-radius:6px; margin:8px 0; font-size:0.8rem;">
                            <div>Buying Cost: <strong>{{ p.cost_buy | round(2) }} ETB</strong></div>
                            <div>Selling Cost: <strong>{{ p.cost_sell | round(2) }} ETB</strong></div>
                        </div>
                    {% endif %}
                    <div class="product-price">{{ p.cost_sell | round(2) }} ETB</div>
                    <div style="margin-top:auto; padding-top:15px; border-top:1px solid #f1f5f9;">
                        {% if is_authenticated %}
                            {% if is_admin %}
                                <a href="{{ url_for('edit_product_page', id=p.id) }}" class="btn btn-primary btn-sm" style="background:#ea580c; display:block; text-align:center; margin-bottom:5px;">Edit & Update Profile</a>
                                <a href="{{ url_for('delete_product', id=p.id) }}" class="btn btn-danger btn-sm" style="display:block; text-align:center;">Delete Product</a>
                            {% else %}
                                <form action="{{ url_for('buy_product', id=p.id) }}" method="POST" style="display:flex; gap:5px;">
                                    <input type="number" name="buy_qty" class="form-control" value="1" min="1" max="{{ p.quantity }}" style="width:70px; margin-bottom:0; padding:0.4rem;">
                                    <button type="submit" class="btn btn-success btn-sm" style="flex-grow:1;">Buy Now</button>
                                </form>
                            {% endif %}
                        {% else %}
                            <a href="{{ url_for('login') }}" class="btn btn-primary btn-sm" style="display:block; text-align:center; background:#475569;">Sign In to Register / Buy</a>
                        {% endif %}
                    </div>
                </div>
            </div>
            {% else %}
            <div style="grid-column: 1/-1; text-align:center; padding:40px; color:#94a3b8; font-weight:600;">No matching display profiles on market showcase right now.</div>
            {% endfor %}
        </div>
    </div>
    {% if is_merchant_or_admin %}
    <div class="card">
        <h3 style="margin-top:0; border-bottom:2px solid #f1f5f9; padding-bottom:10px; color:#0f172a;">Merchant Businessman Console</h3>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:30px; margin-top:20px;">
            <div>
                <h4 style="margin-top:0; color:#475569;">Step 1: Register Shop Profile</h4>
                <form action="{{ url_for('add_merchant_business') }}" method="POST">
                    <div class="form-group">
                        <label class="form-label">Shop / Businessman Name</label>
                        <input type="text" name="b_name" class="form-control" required placeholder="e.g. Al-Amudi Technology Shop">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Trade License Number</label>
                        <input type="text" name="b_license" class="form-control" required placeholder="e.g. TLD-8899-ET">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Contact Phone Number</label>
                        <input type="text" name="b_phone" class="form-control" required placeholder="e.g. +251...">
                    </div>
                    <input type="hidden" name="b_sector" value="Retail Store Marketplace">
                    <input type="hidden" name="b_owner" value="{{ current_user.username if is_authenticated else '' }}">
                    <button type="submit" class="btn btn-primary">Register Store Profile</button>
                </form>
            </div>
            <div>
                <h4 style="margin-top:0; color:#475569;">Step 2: Add Inventory Product</h4>
                <form action="{{ url_for('add_merchant_product') }}" method="POST">
                    <div class="form-group">
                        <label class="form-label">Select Registered Shop</label>
                        <select name="p_business_id" class="form-select" required>
                            {% for mb in my_businesses %}
                            <option value="{{ mb.id }}">{{ mb.business_name }}</option>
                            {% else %}
                            <option value="">Register a shop first on the left form</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Product Item Name</label>
                        <input type="text" name="p_name" class="form-control" required placeholder="e.g. Samsung Galaxy S24 Ultra">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Product Category</label>
                        <select name="p_category" class="form-select">
                            <option value="Electronics">Electronics</option>
                            <option value="Clothing & Fashion">Clothing & Fashion</option>
                            <option value="Agriculture & Food">Agriculture & Food</option>
                            <option value="Cosmetics & Beauty">Cosmetics & Beauty</option>
                            <option value="Home & Construction">Home & Construction</option>
                        </select>
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                        <div class="form-group">
                            <label class="form-label">Cost of BUY (Cost Price)</label>
                            <input type="number" step="0.01" name="p_buy" class="form-control" required placeholder="ETB">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Cost of SELL (Retail Price)</label>
                            <input type="number" step="0.01" name="p_sell" class="form-control" required placeholder="ETB">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Total Product Stock Quantity</label>
                        <input type="number" name="p_qty" class="form-control" required placeholder="Units count">
                    </div>
                    <button type="submit" class="btn btn-success">Upload Product to Gebeya</button>
                </form>
            </div>
        </div>
    </div>
    {% endif %}
    {% if is_admin %}
    <div class="card">
        <h3 style="margin-top:0; border-bottom:2px solid #f1f5f9; padding-bottom:10px; color:#ea580c;">Administrative Database Ledgers</h3>
        <h5 style="margin-bottom:10px; color:#475569;">All System Orders History</h5>
        <div class="table-responsive" style="margin-bottom:25px;">
            <table>
                <thead>
                    <tr>
                        <th>Order ID</th>
                        <th>Buyer Username</th>
                        <th>Product Purchased</th>
                        <th>Quantity</th>
                        <th>Total Transaction Price</th>
                        <th>Transaction Date</th>
                    </tr>
                </thead>
                <tbody>
                    {% for o in all_orders %}
                    <tr>
                        <td>{{ o.id }}</td>
                        <td><strong>{{ o.buyer.username if o.buyer else 'Deleted User' }}</strong></td>
                        <td>{{ o.product_profile.product_name if o.product_profile else 'Deleted Product' }}</td>
                        <td>{{ o.quantity_bought }} units</td>
                        <td><strong style="color:#16a34a;">{{ o.total_price | round(2) }} ETB</strong></td>
                        <td>{{ o.order_date.strftime('%Y-%m-%d %H:%M') if o.order_date else 'N/A' }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="text-center" style="color:#94a3b8; padding:20px;">No transaction history found.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <h5 style="margin-bottom:10px; color:#475569;">System Clerk Directory</h5>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Username</th>
                        <th>Clearance Authorization Role</th>
                        <th>Administrative Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in user_list %}
                    <tr>
                        <td>{{ u.id }}</td>
                        <td><strong>{{ u.username }}</strong></td>
                        <td><span class="role-badge" style="background:{{ '#ea580c' if u.role == 'Admin' else '#64748b' }};color:white;">{{ u.role }}</span></td>
                        <td>
                            {% if is_authenticated and u.id != current_user.id %}
                            <a href="{{ url_for('delete_system_user', id=u.id) }}" class="btn btn-danger btn-sm">Purge Account</a>
                            {% else %}
                            <span style="color:#94a3b8; font-style:italic;">Active Session</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}
    {% endblock %}
    """, total_users=total_users, total_products=total_products, total_orders=total_orders, product_list=product_list, business_list=business_list, user_list=user_list, all_orders=all_orders, search_q=search_q, category_filter=category_filter, my_businesses=my_businesses, is_authenticated=is_authenticated, is_admin=is_admin, is_merchant_or_admin=is_merchant_or_admin)

@app.route('/add_merchant_business', methods=['POST'])
@login_required
def add_merchant_business():
    name = request.form.get('b_name')
    license = request.form.get('b_license')
    sector = request.form.get('b_sector')
    owner = request.form.get('b_owner')
    phone = request.form.get('b_phone')
    try:
        duplicate = db.session.execute(db.select(Business).filter_by(license_number=license)).scalar_one_or_none()
        if duplicate:
            flash(f'Error: License {license} already registered!', 'error')
        else:
            new_store = Business(business_name=name, license_number=license, sector=sector, owner_name=owner, phone_number=phone, user_id=current_user.id)
            db.session.add(new_store)
            db.session.commit()
            flash(f'Store Profile "{name}" successfully opened in marketplace.', 'success')
    except Exception:
        db.session.rollback()
        flash('Database processing error.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/add_merchant_product', methods=['POST'])
@login_required
def add_merchant_product():
    biz_id = request.form.get('p_business_id')
    name = request.form.get('p_name')
    cat = request.form.get('p_category')
    buy = float(request.form.get('p_buy', 0.0))
    sell = float(request.form.get('p_sell', 0.0))
    qty = int(request.form.get('p_qty', 0))
    
    if not biz_id:
        flash('Error: You must create and link a store folder first!', 'error')
        return redirect(url_for('dashboard'))

    biz = db.session.get(Business, int(biz_id))
    if not biz or (biz.user_id != current_user.id and getattr(current_user, 'role', '') != 'Admin'):
        flash('Unauthorized business specified.', 'error')
        return redirect(url_for('dashboard'))

    try:
        new_prod = Product(product_name=name, category=cat, cost_buy=buy, cost_sell=sell, quantity=qty, business_id=int(biz_id))
        db.session.add(new_prod)
        db.session.commit()
        flash(f'Product "{name}" added to showcase registry.', 'success')
    except Exception:
        db.session.rollback()
        flash('Inventory creation error mapping columns.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/buy_product/<int:id>', methods=['POST'])
@login_required
def buy_product(id):
    qty_to_buy = int(request.form.get('buy_qty', 1))
    target_product = db.session.get(Product, id)
    if not target_product:
        flash('Product not found.', 'error')
        return redirect(url_for('dashboard'))

    if target_product.quantity < qty_to_buy:
        flash(f'Insufficient marketplace quantities. Only {target_product.quantity} items left.', 'error')
    else:
        try:
            target_product.quantity -= qty_to_buy
            tot_price = qty_to_buy * target_product.cost_sell
            new_order = Order(user_id=current_user.id, product_id=target_product.id, quantity_bought=qty_to_buy, total_price=tot_price)
            db.session.add(new_order)
            db.session.commit()
            flash(f'Transaction complete! Purchased {qty_to_buy} units of {target_product.product_name}.', 'success')
        except Exception:
            db.session.rollback()
            flash('Checkout operational crash.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/edit_product_page/<int:id>')
@login_required
def edit_product_page(id):
    if getattr(current_user, 'role', '') != 'Admin':
        flash('Unauthorized permissions.', 'error')
        return redirect(url_for('dashboard'))
    p = db.session.get(Product, id)
    if not p:
        flash('Product not found.', 'error')
        return redirect(url_for('dashboard'))

    return render_template_string(BASE_LAYOUT + """
    <div class="card" style="max-width: 500px; margin: 40px auto;">
        <h3 style="margin-top:0; color:#ea580c;">Administrative Product Editor</h3>
        <form action="{{ url_for('update_product', id=p.id) }}" method="POST">
            <div class="form-group">
                <label class="form-label">Product Name</label>
                <input type="text" name="p_name" class="form-control" value="{{ p.product_name }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Category</label>
                <input type="text" name="p_cat" class="form-control" value="{{ p.category }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Stock Quantity Available</label>
                <input type="number" name="p_qty" class="form-control" value="{{ p.quantity }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Cost of BUY (ETB)</label>
                <input type="number" step="0.01" name="p_buy" class="form-control" value="{{ p.cost_buy }}" required>
            </div>
            <div class="form-group">
                <label class="form-label">Cost of SELL (ETB)</label>
                <input type="number" step="0.01" name="p_sell" class="form-control" value="{{ p.cost_sell }}" required>
            </div>
            <div style="display:flex; gap:10px;">
                <button type="submit" class="btn btn-success">Update Entry Data</button>
                <a href="{{ url_for('dashboard') }}" class="btn btn-danger" style="line-height:2.3; background:#64748b;">Cancel</a>
            </div>
        </form>
    </div>
    """, p=p)

@app.route('/update_product/<int:id>', methods=['POST'])
@login_required
def update_product(id):
    if getattr(current_user, 'role', '') != 'Admin':
        flash('Unauthorized entry permissions level.', 'error')
        return redirect(url_for('dashboard'))
    try:
        p = db.session.get(Product, id)
        if not p:
            flash('Product not found.', 'error')
            return redirect(url_for('dashboard'))

        p.product_name = request.form.get('p_name')
        p.category = request.form.get('p_cat')
        p.quantity = int(request.form.get('p_qty', 0))
        p.cost_buy = float(request.form.get('p_buy', 0.0))
        p.cost_sell = float(request.form.get('p_sell', 0.0))
        db.session.commit()
        flash('Product configuration successfully updated by Administration.', 'success')
    except Exception:
        db.session.rollback()
        flash('Operational update failure.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_product/<int:id>')
@login_required
def delete_product(id):
    if getattr(current_user, 'role', '') != 'Admin':
        flash('Unauthorized permissions level.', 'error')
        return redirect(url_for('dashboard'))
    try:
        p = db.session.get(Product, id)
        if p:
            db.session.delete(p)
            db.session.commit()
            flash('Product profile successfully dropped from marketplace.', 'success')
        else:
            flash('Product not found.', 'error')
    except Exception:
        db.session.rollback()
        flash('Purge failure.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_system_user/<int:id>')
@login_required
def delete_system_user(id):
    if getattr(current_user, 'role', '') != 'Admin':
        flash('Unauthorized administration clearance.', 'error')
        return redirect(url_for('dashboard'))
    try:
        u = db.session.get(User, id)
        if u:
            db.session.delete(u)
            db.session.commit()
            flash('User database matrix row removed.', 'success')
        else:
            flash('User not found.', 'error')
    except Exception:
        db.session.rollback()
        flash('Purge failure.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out cleanly from platform workspace.', 'success')
    return redirect(url_for('login'))

# --- APPLICATION INITIALIZATION ---

with app.app_context():
    db.create_all()
    try:
        admin_user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                username='admin', 
                password=generate_password_hash('admin123'), 
                role='Admin'
            )
            db.session.add(admin_user)
            db.session.commit()
    except Exception:
        db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)

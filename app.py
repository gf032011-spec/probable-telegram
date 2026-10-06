import osfrom datetime import datetime, timezonefrom flask import Flask, render_template_string, redirect, url_for, request, flashfrom flask_sqlalchemy import SQLAlchemyfrom flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_userfrom werkzeug.security import generate_password_hash, check_password_hash
# --- APPLICATION SETUP ---app = Flask(__name__)# Uses a safe environment variable key fallback
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zemene-gebeya-super-secret-key-112233')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)login_manager = LoginManager(app)
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

@login_manager.user_loaderdef load_user(user_id):
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
</html>"""
# --- ROUTES ---

@app.route('/')def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])def login():
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
{% block content %}


Account Login

Login


New to the market? Create Account



{% endblock %}
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
{% block content %}


Create Market Account

Standard Customer (Buy Products)
Merchant Businessman (Register Products)
System Administrator (Edit & Update All)


Sign Up


Back to Login



{% endblock %}
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


{{ total_products }}
Total Products on Display


{{ total_orders }}
Successful Transactions Executed


{{ total_users }}
Active Registered Market Entities




Zemene Gebeya Market Showcase
Interactive visual stock listings directory


All Categories
<option value="Electronics" {% if category_filter == 'Electronics' %}selected{% endif %}>Electronics
<option value="Clothing & Fashion" {% if category_filter == 'Clothing & Fashion' %}selected{% endif %}>Clothing & Fashion
<option value="Agriculture & Food" {% if category_filter == 'Agriculture & Food' %}selected{% endif %}>Agriculture & Food
<option value="Cosmetics & Beauty" {% if category_filter == 'Cosmetics & Beauty' %}selected{% endif %}>Cosmetics & Beauty
<option value="Home & Construction" {% if category_filter == 'Home & Construction' %}selected{% endif %}>Home & Construction



Search
Reset



{% for p in product_list %}

📦

{{ p.category }}
{{ p.product_name }}
Shop Vendor: {{ p.associated_shop.business_name if p.associated_shop else 'N/A' }}
Total Stock Available: {{ p.quantity }} units
{% if is_merchant_or_admin %}

Buying Cost: {{ p.cost_buy | round(2) }} ETB
Selling Cost: {{ p.cost_sell | round(2) }} ETB

{% endif %}
{{ p.cost_sell | round(2) }} ETB

{% if is_authenticated %}
{% if is_merchant_or_admin %}
Edit Profile
Delete Product
{% else %}


Buy Now

{% endif %}
{% else %}
Sign In to Buy
{% endif %}



{% else %}
No matching display profiles on market showcase right now.
{% endfor %}


{% if is_merchant_or_admin %}

Merchant Businessman Console


Step 1: Register Shop Profile

Register Store Profile



Step 2: Add Inventory Product

{% for mb in my_businesses %}
{{ mb.business_name }}
{% else %}
Register a shop first on the left form
{% endfor %}


Electronics
Clothing & Fashion
Agriculture & Food
Cosmetics & Beauty
Home & Construction



Upload Product to Gebeya




{% endif %}
{% if is_admin %}

Administrative Database Ledgers
All System Orders History
System Clerk Directory
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
@app.route('/buy_product/int:id', methods=['POST'])
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
@app.route('/edit_product_page/int:id')
@login_required
def edit_product_page(id):
p = db.session.get(Product, id)
if not p:
flash('Product not found.', 'error')
return redirect(url_for('dashboard'))
# Ensure Merchants only edit their own shop product, Admins can edit anything
if getattr(current_user, 'role', '') != 'Admin' and p.associated_shop.user_id != current_user.id:
flash('Unauthorized permissions.', 'error')
return redirect(url_for('dashboard'))
return render_template_string(BASE_LAYOUT + """
{% block content %}

Product Profile Editor

Update Entry Data
Cancel



{% endblock %}
""", p=p)
@app.route('/update_product/int:id', methods=['POST'])
@login_required
def update_product(id):
try:
p = db.session.get(Product, id)
if not p:
flash('Product not found.', 'error')
return redirect(url_for('dashboard'))
if getattr(current_user, 'role', '') != 'Admin' and p.associated_shop.user_id != current_user.id:
flash('Unauthorized entry permissions level.', 'error')
return redirect(url_for('dashboard'))
p.product_name = request.form.get('p_name')
p.category = request.form.get('p_cat')
p.quantity = int(request.form.get('p_qty', 0))
p.cost_buy = float(request.form.get('p_buy', 0.0))
p.cost_sell = float(request.form.get('p_sell', 0.0))
db.session.commit()
flash('Product configuration successfully updated.', 'success')
except Exception:
db.session.rollback()
flash('Operational update failure.', 'error')
return redirect(url_for('dashboard'))
@app.route('/delete_product/int:id')
@login_required
def delete_product(id):
try:
p = db.session.get(Product, id)
if not p:
flash('Product not found.', 'error')
return redirect(url_for('dashboard'))
if getattr(current_user, 'role', '') != 'Admin' and p.associated_shop.user_id != current_user.id:
flash('Unauthorized permissions level.', 'error')
return redirect(url_for('dashboard'))
db.session.delete(p)
db.session.commit()
flash('Product profile successfully dropped from marketplace.', 'success')
except Exception:
db.session.rollback()
flash('Purge failure.', 'error')
return redirect(url_for('dashboard'))
@app.route('/delete_system_user/int:id')
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
## --- APPLICATION INITIALIZATION ---
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
if name == 'main':
app.run(debug=True)


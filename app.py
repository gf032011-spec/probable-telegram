import os
from datetime import datetime, timezone
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'zemene-gebeya-super-secret-key-112233')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'online_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
os.makedirs(app.instance_path, exist_ok=True)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
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
            
    return render_template('login.html')
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
            
    return render_template('register.html')
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

    return render_template('dashboard.html', total_users=total_users, total_products=total_products, total_orders=total_orders, product_list=product_list, business_list=business_list, user_list=user_list, all_orders=all_orders, search_q=search_q, category_filter=category_filter, my_businesses=my_businesses, is_authenticated=is_authenticated, is_admin=is_admin, is_merchant_or_admin=is_merchant_or_admin)
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
    return render_template('edit_product.html', p=p)

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
with app.app_context():
    db.create_all()
    try:
        admin_user = db.session.execute(db.select(User).filter_by(username='admin')).scalar_one_or_none()
        if not admin_user:
            admin_user = User(username='admin', password=generate_password_hash('admin123'), role='Admin')
            db.session.add(admin_user)
            db.session.commit()
    except Exception:
        db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True)

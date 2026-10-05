import os
from datetime import datetime
from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trade-office-super-secret-key-98765')

# FORCE STANDARD SYSTEM ROUTE: Stores database file directly in root to prevent folder permission crashes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==========================================
# DATABASE SCHEMAS & MODELS
# ==========================================
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    role = db.Column(db.String(20), nullable=False, default='User')
    businesses = db.relationship('Business', backref='registrar', lazy=True, cascade="all, delete-orphan")

class Business(db.Model):
    __tablename__ = 'Businesses'
    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False)
    license_number = db.Column(db.String(100), unique=True, nullable=False)
    sector = db.Column(db.String(100), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# UNIVERSAL RESPONSIVE GRAPHICAL INTERFACE
# ==========================================
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gelan Guda Sub City Trade Office</title>
    <style>
        body { background-color: #f0f2f5; font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; color: #333333; }
        .navbar { background: #1e293b; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar h2 { margin: 0; font-size: 1.3rem; font-weight: 700; }
        .nav-links a { color: #cbd5e1; text-decoration: none; margin-left: 15px; font-weight: 500; font-size: 0.95rem; }
        .nav-links a:hover { color: white; }
        .main-container { max-width: 1100px; margin: 40px auto; padding: 0 20px; box-sizing: border-box; }
        .auth-wrapper { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
        .card { background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e3e6ea; width: 100%; box-sizing: border-box; margin-bottom: 30px; }
        .auth-card { max-width: 420px; }
        .text-center { text-align: center; }
        .mb-3 { margin-bottom: 1rem; }
        .mb-4 { margin-bottom: 1.5rem; }
        .mt-3 { margin-top: 1rem; }
        .w-100 { width: 100%; }
        .font-weight-bold { font-weight: bold; }
        .form-group { margin-bottom: 1.25rem; text-align: left; }
        .form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.9rem; color: #475569; }
        .form-control, .form-select { display: block; width: 100%; padding: 0.6rem 0.75rem; font-size: 0.95rem; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
        .btn { display: inline-block; font-weight: 600; text-align: center; cursor: pointer; padding: 0.65rem 1.2rem; font-size: 0.95rem; border-radius: 6px; border: 1px solid transparent; text-decoration: none; box-sizing: border-box; width: 100%; }
        .btn-primary { color: #ffffff; background-color: #007bff; }
        .btn-success { color: #ffffff; background-color: #28a745; }
        .btn-danger { color: #ffffff; background-color: #dc3545; }
        .btn-sm { padding: 0.35rem 0.75rem; font-size: 0.85rem; border-radius: 4px; width: auto; }
        .alert { padding: 0.75rem 1.25rem; margin-bottom: 1.5rem; border-radius: 6px; font-weight: 500; font-size: 0.95rem; }
        .alert-danger { color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .alert-success { color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-box { background: white; padding: 20px; border-radius: 8px; border: 1px solid #e3e6ea; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align: center; }
        .stat-box h3 { margin: 0 0 5px 0; font-size: 2rem; color: #007bff; }
        .stat-box p { margin: 0; color: #64748b; font-weight: 500; font-size: 0.9rem; }
        table { width: 100%; border-collapse: collapse; background: #ffffff; margin-top: 10px; border-radius: 8px; overflow: hidden; }
        th, td { padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid #e3e6ea; font-size: 0.9rem; }
        th { background-color: #f8f9fa; font-weight: 600; color: #475569; }
        .table-responsive { width: 100%; overflow-x: auto; border: 1px solid #e3e6ea; border-radius: 8px; background: white; }
    </style>
</head>
<body>
    {% if current_user.is_authenticated %}
    <div class="navbar">
        <h2>Gelan Guda Trade Office</h2>
        <div class="nav-links">
            <span>Welcome, <strong>{{ current_user.username }}</strong></span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </div>
    {% endif %}

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

# ==========================================
# ROUTES
# ==========================================
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except Exception:
            flash('Database processing error. Please refresh.', 'error')
            
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <div class="auth-wrapper">
        <div class="card auth-card">
            <h3 class="text-center mb-4 font-weight-bold" style="margin-top:0;color:#1e293b;">Account Sign In</h3>
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Enter password">
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            <div class="text-center" style="margin-top: 20px; font-size:0.9rem;">
                <span style="color:#64748b;">New clerk?</span> <a href="/register" style="color:#007bff;text-decoration:none;font-weight:600;">Create Account</a>
            </div>
        </div>
    </div>
    """))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'User')
        try:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already registered in database!', 'error')
            else:
                new_user = User(username=username, password=generate_password_hash(password), role=role)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! Please sign in.', 'success')
                return redirect(url_for('login'))
        except Exception:
            flash('Database registration channel error.', 'error')
            
        return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <div class="auth-wrapper">
        <div class="card auth-card">
            <h3 class="text-center mb-4 font-weight-bold" style="margin-top:0;color:#1e293b;">Account Sign In</h3>
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required placeholder="Enter username">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Enter password">
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            <div class="text-center" style="margin-top: 20px; font-size:0.9rem;">
                <span style="color:#64748b;">New clerk?</span> <a href="/register" style="color:#007bff;text-decoration:none;font-weight:600;">Create Account</a>
            </div>
        </div>
    </div>
    """))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'User')
        try:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already registered in database!', 'error')
            else:
                new_user = User(username=username, password=generate_password_hash(password), role=role)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! Please sign in.', 'success')
                return redirect(url_for('login'))
        except Exception:
            flash('Database registration channel error.', 'error')
            
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <div class="auth-wrapper">
        <div class="card auth-card">
            <h3 class="text-center mb-4 font-weight-bold" style="margin-top:0;color:#1e293b;">Register New Clerk</h3>
            <form method="POST">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" name="username" class="form-control" required placeholder="Create username">
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" name="password" class="form-control" required placeholder="Create secure password">
                </div>
                <div class="form-group">
                    <label class="form-label">Authorization Clearance</label>
                    <select name="role" class="form-select">
                        <option value="User">Standard Clerk (User)</option>
                        <option value="Admin">Office Administrator (Admin)</option>
                    </select>
                </div>
                <button type="submit" class="btn btn-success">Sign Up</button>
            </form>
            <div class="text-center" style="margin-top: 20px; font-size:0.9rem;">
                <a href="/login" style="color:#007bff;text-decoration:none;font-weight:600;">Back to Login</a>
            </div>
        </div>
    </div>
    """))

@app.route('/dashboard')
@login_required
def dashboard():
    total_users = User.query.count()
    total_businesses = Business.query.count()
    
    if current_user.role == 'Admin':
        user_list = User.query.all()
        business_list = Business.query.all()
    else:
        user_list = [current_user]
        business_list = Business.query.filter_by(user_id=current_user.id).all()
        
    return render_template_string(BASE_LAYOUT.replace("{% block content %}{% endblock %}", """
    <div class="stats-grid">
        <div class="stat-box">
            <h3>{{ total_businesses }}</h3>
            <p>Registered Businesses</p>
        </div>
        <div class="stat-box">
            <h3>{{ total_users }}</h3>
            <p>Active System Clerks</p>
        </div>
        <div class="stat-box">
            <h3 style="color:#28a745;">Active</h3>
            <p>Database Matrix Status</p>
        </div>
    </div>

    <div class="card">
        <h4 style="margin-top:0; color:#1e293b; border-bottom:2px solid #f0f2f5; padding-bottom:10px;">Register Business</h4>
        <form action="/add_business" method="POST">
            <div class="form-group">
                <label class="form-label">Business Name</label>
                <input type="text" name="business_name" class="form-control" required placeholder="e.g. Gelan Agro Trading">
            </div>
            <div class="form-group">
                <label class="form-label">License Number</label>
                <input type="text" name="license_number" class="form-control" required placeholder="e.g. BL-2026-XYZ">
            </div>
            <div class="form-group">
                <label class="form-label">Business Sector</label>
                <select name="sector" class="form-select">
                    <option value="Commercial / Trade">Commercial / Trade</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Service Provider">Service Provider</option>
                    <option value="Agriculture">Agriculture</option>
                    <option value="Construction">Construction</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Add to Registry</button>
        </form>
    </div>

    <div class="card">
        <h4 style="margin-top:0; color:#1e293b; border-bottom:2px solid #f0f2f5; padding-bottom:10px;">Trade Registry Database</h4>
        <h5 style="margin-bottom:10px; color:#475569;">Business Records</h5>
        <div class="table-responsive" style="margin-bottom:25px;">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Business Name</th>
                        <th>License #</th>
                        <th>Sector</th>
                        <th>Clerk</th>
                        {% if current_user.role == 'Admin' %}<th>Actions</th>{% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for b in business_list %}
                    <tr>
                        <td>{{ b.id }}</td>
                        <td><strong>{{ b.business_name }}</strong></td>
                        <td><code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;">{{ b.license_number }}</code></td>
                        <td>{{ b.sector }}</td>
                        <td>{{ b.registrar.username }}</td>
                        {% if current_user.role == 'Admin' %}
                        <td>
                            <a href="/delete_business/{{ b.id }}" class="btn btn-danger btn-sm">Delete</a>
                        </td>
                        {% endif %}
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="text-center" style="color:#94a3b8; padding:20px;">No business profiles found in registry database.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <h5 style="margin-bottom:10px; color:#475569;">Office Clerk Directory</h5>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Username</th>
                        <th>System Role</th>
                        {% if current_user.role == 'Admin' %}<th>Administrative Action</th>{% endif %}
                    </tr>
                </thead>
                <tbody>
                    {% for u in user_list %}
                    <tr>
                        <td>{{ u.id }}</td>
                        <td>{{ u.username }}</td>
                        <td>
                            <span style="padding:3px 8px; border-radius:12px; font-size:0.8rem; font-weight:bold; background:{{ '#dbeafe;color:#1e40af;' if u.role == 'Admin' else '#f1f5f9;color:#475569;' }}">
                                {{ u.role }}
                            </span>
                        </td>
                        {% if current_user.role == 'Admin' %}
                        <td>
                            {% if u.id != current_user.id %}
                            <a href="/delete_user/{{ u.id }}" class="btn btn-danger btn-sm">Remove</a>
                            {% else %}
                            <span style="color:#94a3b8; font-size:0.85rem; font-style:italic;">Current Session</span>
                            {% endif %}
                        </td>
                        {% endif %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    """), total_users=total_users, total_businesses=total_businesses, user_list=user_list, business_list=business_list)
@app.route('/add_business', methods=['POST'])
@login_required
def add_business():
    b_name = request.form.get('business_name')
    b_license = request.form.get('license_number')
    b_sector = request.form.get('sector')
    try:
        duplicate = Business.query.filter_by(license_number=b_license).first()
        if duplicate:
            flash(f'Error: License number {b_license} already exists!', 'error')
        else:
            new_biz = Business(business_name=b_name, license_number=b_license, sector=b_sector, user_id=current_user.id)
            db.session.add(new_biz)
            db.session.commit()
            flash(f'Business "{b_name}" registered successfully!', 'success')
    except Exception:
        db.session.rollback()
        flash('Error executing transaction.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_business/<int:id>')
@login_required
def delete_business(id):
    if current_user.role != 'Admin':
        flash('Unauthorized permission level.', 'error')
        return redirect(url_for('dashboard'))
    try:
        target = Business.query.get_or_404(id)
        db.session.delete(target)
        db.session.commit()
        flash('Business record removed from active registry data rows.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error executing row purge.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:id>')
@login_required
def delete_user(id):
    if current_user.role != 'Admin':
        flash('Unauthorized permission level.', 'error')
        return redirect(url_for('dashboard'))
    if id == current_user.id:
        flash('Cannot terminate active system session.', 'error')
        return redirect(url_for('dashboard'))
    try:
        target = User.query.get_or_404(id)
        db.session.delete(target)
        db.session.commit()
        flash('User token entity successfully removed.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error executing row purge.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# Isolated execution architecture seeding thread
with app.app_context():
    db.create_all()
    try:
        if not User.query.filter_by(username='admin').first():
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


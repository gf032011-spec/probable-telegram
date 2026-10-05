import os
from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'local-secret-key-12345')

# 1. FIXED DATABASE PATH: Auto-detects Render storage versus local environment seamlessly
if os.path.exists('/data') or os.environ.get('RENDER'):
    try:
        os.makedirs('/data', exist_ok=True)
    except Exception:
        pass
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/online_database.db'
else:
    os.makedirs('data', exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/online_database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==========================================
# DATABASE MODEL
# ==========================================
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    role = db.Column(db.String(20), nullable=False, default='User')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==========================================
# HTML LAYOUT (FIXED DESIGN)
# ==========================================
BASE_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Web Application</title>
    <style>
        body { background-color: #f0f2f5; font-family: system-ui, -apple-system, sans-serif; display: flex; justify-content: center; padding-top: 60px; color: #333333; }
        .card { background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 420px; border: 1px solid #e3e6ea; box-sizing: border-box; }
        .text-center { text-align: center; }
        .mb-3 { margin-bottom: 1rem; }
        .mb-4 { margin-bottom: 1.5rem; }
        .mt-3 { margin-top: 1rem; }
        .w-100 { width: 100%; }
        .font-weight-bold { font-weight: bold; }
        .form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; font-size: 0.95rem; text-align: left; }
        .form-control, .form-select { display: block; width: 100%; padding: 0.5rem 0.75rem; font-size: 1rem; border: 1px solid #cccccc; border-radius: 6px; box-sizing: border-box; margin-bottom: 1rem; }
        .btn { display: inline-block; font-weight: 600; text-align: center; cursor: pointer; padding: 0.6rem 1.2rem; font-size: 1rem; border-radius: 6px; border: 1px solid transparent; text-decoration: none; box-sizing: border-box; width: 100%; }
        .btn-primary { color: #ffffff; background-color: #007bff; }
        .btn-success { color: #ffffff; background-color: #28a745; }
        .btn-danger { color: #ffffff; background-color: #dc3545; }
        .alert { padding: 0.75rem 1.25rem; margin-bottom: 1rem; border: 1px solid transparent; border-radius: 6px; font-weight: 500; }
        .alert-danger { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
        .alert-success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
        table { width: 100%; margin-top: 1rem; border-collapse: collapse; background: #ffffff; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background-color: #f8f9fa; font-weight: 600; }
    </style>
</head>
<body class="bg-light">
    <div class="container" style="width:100%; max-width:440px; padding:10px;">
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
            flash('Database configuration updating. Please refresh.', 'error')
            
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card">
        <h3 class="text-center mb-4 font-weight-bold">Account Login</h3>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <div class="text-center mt-3">
            <a href="{{ url_for('register') }}">Create New Account</a>
        </div>
    </div>
    {% endblock %}
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        try:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists!', 'error')
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password=hashed_password, role=role)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created successfully! Please log in.')
                return redirect(url_for('login'))
        except Exception:
            flash('Database processing error.', 'error')
            
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card">
        <h3 class="text-center mb-4 font-weight-bold">Register</h3>
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Account Type</label>
                <select name="role" class="form-select">
                    <option value="User">User</option>
                    <option value="Admin">Admin</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success">Sign Up</button>
        </form>
        <div class="text-center mt-3">
            <a href="{{ url_for('login') }}">Back to Login</a>
        </div>
    </div>
    {% endblock %}
    """)

@app.route('/dashboard')
@login_required
def dashboard():
    all_users = []
    try:
        if current_user.role == 'Admin':
            all_users = User.query.all()
    except Exception:
        pass
        
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card" style="max-width: 100%; width: 600px;">
        <h3 class="mb-3">Welcome, {{ current_user.username }} ({{ current_user.role }})</h3>
        
        {% if current_user.role == 'Admin' %}
            <h5>Registered Database Entities:</h5>
            <table>
                <thead>
                    <tr>
                        <th>User ID</th>
                        <th>Username</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in all_users %}
                    <tr>
                        <td>{{ u.id }}</td>
                        <td>{{ u.username }}</td>
                        <td>{{ u.role }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <p class="lead mt-4 text-muted">Standard access level verified. You can navigate standard application parameters.</p>
        {% endif %}
        
        <a href="{{ url_for('logout') }}" class="btn btn-danger mt-4">Logout</a>
    </div>
    {% endblock %}
    """, all_users=all_users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Automated initialization logic block
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

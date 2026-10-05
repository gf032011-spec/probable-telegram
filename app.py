import os
from flask import Flask, render_template_string, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'local-secret-key-12345')

if not os.path.exists('/data') and not os.environ.get('RENDER'):
    os.makedirs('data', exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/online_database.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/online_database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  
    role = db.Column(db.String(20), nullable=False, default='User')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

BASE_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Web Application</title>
        <link rel="stylesheet" href="https://picocss.com">
</head>
<body class="bg-light">
    <div class="container mt-5" style="max-width: 600px;">
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
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card p-4 shadow-sm text-dark">
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
            <button type="submit" class="btn btn-primary w-100">Login</button>
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
            
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card p-4 shadow-sm text-dark">
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
            <button type="submit" class="btn btn-success w-100">Sign Up</button>
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
    if current_user.role == 'Admin':
        all_users = User.query.all()
        
    return render_template_string(BASE_LAYOUT + """
    {% block content %}
    <div class="card p-4 shadow-sm text-dark">
        <h3 class="mb-3">Welcome, {{ current_user.username }} ({{ current_user.role }})</h3>
        
        {% if current_user.role == 'Admin' %}
            <h5>Registered Database Entities:</h5>
            <table class="table table-striped mt-3">
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('admin123'), role='Admin'))
            db.session.commit()
            
    app.run(debug=True)

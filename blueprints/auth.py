
from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_app.setup_db import User, db_session

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = db_session.query(User).filter(User.username == username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!", "info")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "error")
            
    return render_template('login.html', hide_navbar=True)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, password=hashed_password)
        try:
            db_session.add(new_user)
            db_session.commit()
            flash("Signup successful! Please log in.", "info")
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db_session.rollback()
            flash("Username already exists. Please choose a different username.", "error")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template('signup.html', hide_navbar=True)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('auth.login'))
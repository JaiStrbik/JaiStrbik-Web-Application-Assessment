from flask import Flask, render_template, request, redirect, url_for, session, flash, models
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User  # Import User model

# Database setup
engine = create_engine('sqlite:///yourdatabase.db')
Session = sessionmaker(bind=engine)
db_session = Session()
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secure key for session security

engine = create_engine('sqlite:///yourdatabase.db') #database connection
Session = sessionmaker(bind=engine)
db_session = Session()


app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])  # Add POST method here
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    
        # Query the database to find the user with the given username
        user = db_session.query(User).filter_by(username=username).first()

        # Check if the user exists and if the password matches
        if user and check_password_hash(user.password, password):
            # Store user information in the session
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "info")
            return redirect(url_for("dashboard"))  # Redirect to the dashboard
        else:
            flash("Invalid username or password", "danger")
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])  # Add POST method for signup
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username already exists
        if db_session.query(User).filter_by(username=username).first():
            flash("Username already taken", "danger")
        else:
            # Create a new user with hashed password
            new_user = User(username=username)
            new_user.set_password(password)
            db_session.add(new_user)
            db_session.commit()
            flash("Signup successful! You can now log in.", "info")
            return redirect(url_for("login"))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in by verifying the session data
    if 'user_id' not in session:
        flash("Please login to access the dashboard", "warning")
        return redirect(url_for("login"))
    # Render the dashboard template and pass the user's information from the session
    return render_template('dashboard.html', user_id=session['user_id'], username=session['username'])

@app.route('/logout')
def logout():
    # Clear all data in the session
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)

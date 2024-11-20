from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError  # Import IntegrityError
from setup_db import User, ToDo  # Import the User model

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Secure key for session security

# Database setup
engine = create_engine('sqlite:///todo.db')  # Database connection
Session = sessionmaker(bind=engine)
db_session = Session()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = db_session.query(User).filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username  # Set username in session
            flash("You have successfully logged in", "info")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "error")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        new_user = User(username=username, password=password)
        try:
            db_session.add(new_user)
            db_session.commit()
            flash("Registration successful. Please log in.", "info")
            return redirect(url_for('login'))
        except IntegrityError:
            db_session.rollback()
            flash("Username already exists. Please choose a different username.", "error")
            
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access this dashboard", "warning")
        return redirect(url_for('login'))
    user_id = session["user_id"]
    todos = db_session.query(ToDo).filter_by(user_id=user_id).all()
    username = session.get("username", "Guest")
    return render_template("dashboard.html", user_id=user_id, username=username, todos=todos)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task_page():
    if "user_id" not in session:
        flash("Please log in to add a task", "warning")
        return redirect(url_for('login'))
    if request.method == "POST":
        task_content = request.form.get('content')
        new_task = ToDo(content=task_content, user_id=session['user_id'])
        db_session.add(new_task)
        db_session.commit()
        flash("Task added successfully", "info")
        return redirect(url_for('dashboard'))
    return render_template('add_task.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
    





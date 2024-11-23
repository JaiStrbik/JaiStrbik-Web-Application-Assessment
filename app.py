from flask import Flask, request, redirect, url_for, render_template, session, flash
from setup_db import User, ToDo, db_session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
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
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
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
            return redirect(url_for('login'))
        except IntegrityError:
            db_session.rollback()
            flash("Username already exists. Please choose a different username.", "error")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            
    return render_template('signup.html')

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if "user_id" not in session:
        flash("Please log in to add a task", "warning")
        return redirect(url_for('login'))
    if request.method == "POST":
        task_name = request.form.get('taskName')
        task_description = request.form.get('taskDescription')
        task_category = request.form.get('taskCategory')
        new_task = ToDo(name=task_name, description=task_description, category=task_category, user_id=session['user_id'], completed=False)
        try:
            db_session.add(new_task)
            db_session.commit()
            flash("Task added successfully", "info")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))
    return render_template('add_task.html')

@app.route('/dashboard')
def dashboard():
    if "user_id" not in session:
        flash("Please log in to view the dashboard", "warning")
        return redirect(url_for('login'))
    tasks = db_session.query(ToDo).filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', tasks=tasks)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if "user_id" not in session:
        flash("Please log in to edit a task", "warning")
        return redirect(url_for('login'))
    task = db_session.query(ToDo).filter_by(id=task_id, user_id=session['user_id']).first()
    if request.method == "POST":
        task.name = request.form.get('taskName')
        task.description = request.form.get('taskDescription')
        task.category = request.form.get('taskCategory')
        task.completed = 'completed' in request.form
        try:
            db_session.commit()
            flash("Task updated successfully", "info")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if "user_id" not in session:
        flash("Please log in to delete a task", "warning")
        return redirect(url_for('login'))
    task = db_session.query(ToDo).filter_by(id=task_id, user_id=session['user_id']).first()
    try:
        db_session.delete(task)
        db_session.commit()
        flash("Task deleted successfully", "info")
    except Exception as e:
        db_session.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)





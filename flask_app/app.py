from flask import Flask, request, redirect, url_for, render_template, session, flash
import os
from setup_db import User, ToDo, db_session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy import extract
from datetime import datetime, date
import re

app = Flask(__name__, 
           static_url_path='/static',  # Serve static files from /static URL
           static_folder='static')  # Point to static folder
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('landing.html')

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

        # Validate password requirements
        if not (re.search(r'[A-Za-z]', password) and  # at least one letter
                re.search(r'[0-9]', password) and      # at least one number
                re.search(r'[!@#$%^&*(),.?":{}|<>]', password)): # at least one symbol
            flash("Password must contain at least one letter, one number, and one symbol", "error")
            return redirect(url_for('signup'))

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
        due_date = request.form.get('dueDate')
        due_time = request.form.get('dueTime')
        
        if not due_date or not due_time:
            flash("Due date and time are required", "error")
            return redirect(url_for('add_task'))
        
        try:
            due_datetime = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Invalid date or time format", "error")
            return redirect(url_for('add_task'))
        
        new_task = ToDo(name=task_name, description=task_description, category=task_category, user_id=session['user_id'], completed=False, due_date=due_datetime)
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
    
    current_time = datetime.now()
    tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=False).all()
    completed_tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=True).all()
    overdue_tasks = [task for task in tasks if task.due_date < current_time]
    
    # Function to convert ToDo object to dictionary
    def serialize_task(task):
        return {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'category': task.category,
            'due_date': task.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'completed': task.completed
        }

    # Convert all tasks to dictionaries
    serialized_tasks = [serialize_task(task) for task in tasks]
    serialized_completed = [serialize_task(task) for task in completed_tasks]
    serialized_overdue = [serialize_task(task) for task in overdue_tasks]
    
    return render_template('dashboard.html', 
                         tasks=tasks,  # Original tasks for normal rendering
                         completed_tasks=completed_tasks,  # Original tasks for normal rendering
                         overdue_tasks=overdue_tasks,  # Original tasks for normal rendering
                         tasks_json=serialized_tasks,  # Serialized tasks for JavaScript
                         completed_tasks_json=serialized_completed,  # Serialized tasks for JavaScript
                         overdue_tasks_json=serialized_overdue)  # Serialized tasks for JavaScript

@app.route('/completed_tasks')
def view_completed_tasks():
    if "user_id" not in session:
        flash("Please log in to view completed tasks", "warning")
        return redirect(url_for('login'))
    
    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Query for tasks completed this month
    tasks_this_month = db_session.query(ToDo).filter(
        ToDo.user_id == session['user_id'],
        ToDo.completed == True,
        extract('month', ToDo.due_date) == current_month,
        extract('year', ToDo.due_date) == current_year
    ).all()
    
    # Query for all completed tasks grouped by category
    tasks_by_category = {}
    all_completed_tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=True).all()
    for task in all_completed_tasks:
        if task.category not in tasks_by_category:
            tasks_by_category[task.category] = []
        tasks_by_category[task.category].append(task)
    
    return render_template('completed_tasks.html', tasks_this_month=tasks_this_month, tasks_by_category=tasks_by_category)

@app.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    if "user_id" not in session:
        flash("Please log in to complete a task", "warning")
        return redirect(url_for('login'))
    task = db_session.query(ToDo).filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        task.completed = True
        try:
            db_session.commit()
            flash("Task marked as completed", "info")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
    return redirect(url_for('dashboard'))

@app.route('/uncomplete_task/<int:task_id>', methods=['POST'])
def uncomplete_task(task_id):
    if "user_id" not in session:
        flash("Please log in to uncomplete a task", "warning")
        return redirect(url_for('login'))
    task = db_session.query(ToDo).filter_by(id=task_id, user_id=session['user_id']).first()
    if task:
        task.completed = False
        try:
            db_session.commit()
            flash("Task marked as not completed", "info")
        except Exception as e:
            db_session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
    return redirect(url_for('view_completed_tasks'))

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
        due_date = request.form.get('dueDate')
        due_time = request.form.get('dueTime')
        
        if not due_date or not due_time:
            flash("Due date and time are required", "error")
            return redirect(url_for('edit_task', task_id=task_id))
        
        try:
            task.due_date = datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash("Invalid date or time format", "error")
            return redirect(url_for('edit_task', task_id=task_id))
        
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

# Remove or comment out the calendar_view route since we're not using it anymore
# @app.route('/calendar')
# def calendar_view():
#     ...

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)





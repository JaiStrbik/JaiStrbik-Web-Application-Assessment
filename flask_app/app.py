from flask import Flask, request, redirect, url_for, render_template, session, flash, send_from_directory
import os
from setup_db import User, ToDo, db_session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__, 
           static_url_path='/static',  # Serve static files from /static URL
           static_folder='static')  # Point to static folder
app.secret_key = 'your_secret_key'

# Remove the custom_static route handler
# @app.route('/static/<path:filename>')
# def custom_static(filename):
#     print(f"Attempting to serve static file: {filename}")  # Debug log
#     try:
#         return send_from_directory('static', filename)
#     except Exception as e:
#         print(f"Error serving static file: {e}")  # Debug log
#         return str(e), 404

# Remove any existing static route handlers if present
# Flask will handle static files automatically

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
            
    return render_template('login.html', hide_navbar=True)

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
            
    return render_template('signup.html', hide_navbar=True)

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
    tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=False).all()
    return render_template('dashboard.html', tasks=tasks)

def get_task_statistics(tasks):
    stats = {
        'total_completed': len(tasks),
        'categories': {},
        'completion_by_month': {},
    }
    
    for task in tasks:
        # Category stats
        stats['categories'][task.category] = stats['categories'].get(task.category, 0) + 1
        # Monthly stats
        month = task.due_date.strftime('%B %Y')
        stats['completion_by_month'][month] = stats['completion_by_month'].get(month, 0) + 1
    
    return stats

@app.route('/completed_tasks')
def view_completed_tasks():
    if "user_id" not in session:
        flash("Please log in to view completed tasks", "warning")
        return redirect(url_for('login'))
    
    sort_by = request.args.get('sort', 'date_completed')  # default sort by completion date
    order = request.args.get('order', 'desc')
    
    query = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=True)
    
    if sort_by == 'name':
        query = query.order_by(ToDo.name.desc() if order == 'desc' else ToDo.name)
    elif sort_by == 'category':
        query = query.order_by(ToDo.category.desc() if order == 'desc' else ToDo.category)
    elif sort_by == 'due_date':
        query = query.order_by(ToDo.due_date.desc() if order == 'desc' else ToDo.due_date)
    
    tasks = query.all()
    stats = get_task_statistics(tasks)
    
    return render_template('completed_tasks.html', 
                         tasks=tasks, 
                         stats=stats,
                         sort_by=sort_by, 
                         order=order)

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
    if not task:
        flash("Task not found", "error")
        return redirect(url_for('dashboard'))

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
    if not task:
        flash("Task not found", "error")
        return redirect(url_for('dashboard'))

    try:
        db_session.delete(task)
        db_session.commit()
        flash("Task deleted successfully", "info")
    except Exception as e:
        db_session.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    return redirect(url_for('dashboard'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)





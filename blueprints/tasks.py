from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from blueprints.auth import login_required
from flask_app.setup_db import ToDo, db_session
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/dashboard')
@login_required
def dashboard():
    tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=False).all()
    return render_template('dashboard.html', tasks=tasks)

@tasks_bp.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
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

@tasks_bp.route('/completed_tasks')
@login_required
def view_completed_tasks():
    tasks = db_session.query(ToDo).filter_by(user_id=session['user_id'], completed=True).all()
    return render_template('completed_tasks.html', tasks=tasks)

@tasks_bp.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
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

@tasks_bp.route('/uncomplete_task/<int:task_id>', methods=['POST'])
@login_required
def uncomplete_task(task_id):
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

@tasks_bp.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
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

@tasks_bp.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
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
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask_app.setup_db import User, ToDo
from werkzeug.security import generate_password_hash, check_password_hash

# Connect to the database
engine = create_engine('sqlite:///todo.db')
Session = sessionmaker(bind=engine)
session = Session()

# Query all users and their tasks
users = session.query(User).all()
for user in users:
    print(f"User: {user.username}")
    for todo in user.todos:
        print(f' - Task: {todo.name}, Done: {todo.completed}') 

# Example usage of password hashing
hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
print(f"Hashed Password: {hashed_password}")

session.close()  # Close session after everything is done

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from setup_db import User
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
        print(f' - Task: {todo.task}, Done: {todo.done}') 

# Example usage of password hashing
hashed_password = generate_password_hash('password123')
print(f"Hashed Password: {hashed_password}")

# Example user login check
user = session.query(User).filter_by(username='john_doe').first()
if user and check_password_hash(user.password, 'password123'):  # Check stored password hash
    print("Login successful")
else:
    print("Invalid credentials")

session.close()  # Close session after everything is done

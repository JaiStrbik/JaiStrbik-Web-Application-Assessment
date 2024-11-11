from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    todos = relationship('ToDo', back_populates='user')

    # Method to check password
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
# ToDo model
class ToDo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    task = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='todos')

# # Database setup
engine = create_engine('sqlite:///todo.db')
# Base.metadata.create_all(engine)
# print("Database and tables created successfully")






# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Insert users with hashed password
user1 = User(username='john_doe', password=generate_password_hash('password123'))
user2 = User(username='jane_doe', password=generate_password_hash('mypassword'))

session.add(user1)
session.add(user2)
session.commit()

# Insert tasks
task1 = ToDo(task='Learn SQL Alchemy', done=False, user_id=user1.id)
task2 = ToDo(task='Build an app', done=False, user_id=user2.id)

session.add(task1)
session.add(task2)
session.commit()

print("Users and tasks added successfully")

    



 
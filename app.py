from flask import Flask, render_template
from flask import request, redirect, url_for
app = Flask(__name__)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    
        # Query the databse to find the user with the given username
        user = db_session.query(User).filter_by(username=username).first()

        #check if the user exists and if the password matches

        if user and check_password_hash(user.password, password):
         #store user information in the session
         session['user_id'] = user.id
         session['username'] = user.username
         flash("Login sucessful!", "info")
    
    
    
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
    
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models import User

from models import User, db_session
app.secret_key = "supersecretkey" #Secure key for session security



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
            return redirect(url_for("dashboard")) #redirect to the dashboard
        else:
            flash("Invalid username or password", "danger")
        
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')




@app.route('/dashboard')
def dashboard():
    #check if the user is loggin in by verifying the session data
    if 'user_id' not in session:
        flash("Please login to access the dsahboard", "warning")
        return redirect(url_for("login"))
    #render the dashboard template and pass the user's information from the session
    return render_template('dashboard.html', user_id=session['user_id'], username=session['username'])

@app.route('/logout')
def logout():
    #Clear all data in the session
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
    
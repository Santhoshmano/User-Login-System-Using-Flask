from flask import Flask, render_template, request, redirect, url_for, session, logging
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import re

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Olu1989!@'
app.config['MYSQL_DB'] = 'testdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Intialize MySQL
mysql = MySQL(app)



# http://localhost:5000/ - this will be the welcome page. It loops over the img folder to display the pictures in it
@app.route("/")
def welcomepage():
    images = []
    for filename in os.listdir("static/uikit-3.2.1/img"):
        if filename.endswith("banner.jpg"):
            images.append(os.path.join("static/uikit-3.2.1/img", filename))
        else:
            continue
    return render_template('index.html', len = len(images), images=images)


# http://localhost:5000/login/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password_candidate = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        # Fetch one record and return result
        account = cursor.fetchone()

        password = account['password']

        #compare passwords
        if sha256_crypt.verify(password_candidate, password):
        # If account exists in accounts table in out database
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to dashboard
            return redirect(url_for('dashboard'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return render_template('login.html', msg=msg)
    return render_template('login.html', msg='')


# http://localhost:5000/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = sha256_crypt.encrypt(str(request.form['password']))
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s', [username])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)
    else:
    # Show registration form with message (if any)
        return render_template('register.html')


# http://localhost:500/dashboard - this will be the dashboard, only accessible for loggedin users
@app.route('/dashboard')
def dashboard():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('dashboard.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('register'))


# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

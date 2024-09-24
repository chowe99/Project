from flask import Flask, request, render_template, redirect, session, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Update this in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized

# SQLite database configuration
DATABASE = '/tmp/database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        return User(id_=user[0], username=user[1])
    return None

# **1. SQLi Vulnerable Login Route**
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        # Vulnerable to SQL Injection
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cur.execute(query)
        user = cur.fetchone()
        conn.close()

        if user:
            login_user(User(id_=user[0], username=user[1]))
            return redirect(url_for('dashboard'))
        else:
            return "Login failed", 401

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# **2. Dashboard Route**
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome to the dashboard, {current_user.username}! <a href='/communicate'>Communicate with Doc</a>"

# **3. Communicate Route Vulnerable to XSS**
@app.route('/communicate', methods=['POST', 'GET'])
@login_required
def communicate():
    conn = get_db()
    cur = conn.cursor()
    
    # Load all existing comments from the database
    cur.execute("SELECT sender, comment FROM comments")
    comments = cur.fetchall()
    
    # If it's a POST request, add the new message to the comments table
    if request.method == 'POST':
        message = request.form['message']

        # Insert the message into the database
        cur.execute("INSERT INTO comments (sender, comment) VALUES (?, ?)", (current_user.username, message))
        conn.commit()

        # Simulate Doc's response
        doc_reply = "Got your message, Marty!"
        cur.execute("INSERT INTO comments (sender, comment) VALUES (?, ?)", ("Doc", doc_reply))
        conn.commit()

        conn.close()

        return redirect(url_for('communicate'))

    conn.close()
    return render_template('communicate.html', comments=comments)

# **4. Secret Route Accessible Only by Doc**
@app.route('/secret')
def secret():
    # Only accessible if logged in as Doc
    if 'doc_session' in session and session['doc_session'] == True:
        return "This is Doc's secret page with confidential information!"
    else:
        return "Access denied!", 403

# **5. Index Route**
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


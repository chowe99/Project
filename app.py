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
    if request.method == 'POST':
        message = request.form['message']

        conn = get_db()
        cur = conn.cursor()
        # Insert the message into the database
        cur.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (current_user.username, message))
        conn.commit()

        # Send the message to the bot server for processing
        try:
            response = requests.post('http://bot.com:807/process_message', json={'message': message})
            if response.status_code == 200:
                result = response.json()
                doc_reply = result['response']  # Bot's response (including any XSS result)
            else:
                doc_reply = "Failed to get a response from Doc."
        except Exception as e:
            doc_reply = f"Error communicating with Doc's server: {e}"

        conn.close()

        # Return the communicate.html page, showing both Marty's message and Doc's reply
        return render_template('communicate.html', marty_message=message, doc_reply=doc_reply)
    
    return render_template('communicate.html')

# **4. Doc's Bot to Automatically Reply**
@app.route('/doc_process', methods=['POST'])
def doc_process():
    conn = get_db()
    cur = conn.cursor()
    
    # Fetch unprocessed messages
    cur.execute("SELECT * FROM messages WHERE response IS NULL")
    messages = cur.fetchall()

    for message in messages:
        # Send the message to bot.com (which is localhost:807)
        response = requests.post('http://bot.com:807/process_message', json={'message': message[2]})
        
        if response.status_code == 200:
            result = response.json()
            doc_response = result['response']
            doc_cookie = result['doc_cookie']
            
            # Store Doc's response in the database (or process it further)
            cur.execute("UPDATE messages SET response = ? WHERE id = ?", (doc_response, message[0]))
            conn.commit()

            # Print or exfiltrate Doc's cookie
            print(f"Doc's session/cookie: {doc_cookie}")
    
    conn.close()
    return "Doc has processed the messages."

# **5. Secret Route Accessible Only by Doc**
@app.route('/secret')
def secret():
    # Only accessible if logged in as Doc
    if 'doc_session' in session and session['doc_session'] == True:
        return "This is Doc's secret page with confidential information!"
    else:
        return "Access denied!", 403

# **6. Index Route**
@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


from flask import Flask, request, render_template, redirect, session, url_for, send_from_directory, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Update this in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized

# SQLite database configuration
DATABASE = '/tmp/database.db'

# Directory containing Back to the Future-themed files
DELOREAN_FOLDER = '/app/delorean_files'

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
            session['doc_session'] = True if username == 'doc' else False
            return redirect(url_for('index'))
        else:
            return "Login failed", 401

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# **2. Directory Traversal Vulnerability Route**
@app.route('/file', methods=['POST'])
@login_required
def file():
    filename = f"/app/delorean_files/{request.form.get('filename')}"
    if not filename:
        return "No file selected.", 400

    # Vulnerable to directory traversal - allows user input for file paths
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return f"Contents of {filename.split('/')[3]}:<br><pre>{content}</pre>"
    except FileNotFoundError:
        return f"File not found: {filename}", 404
    except Exception as e:
        return f"Error reading file: {e}", 500

# **3. Dynamic File Listing for Dropdown Menu**
@app.route('/list_files')
@login_required
def list_files():
    path = request.args.get('path', DELOREAN_FOLDER)
    try:
        # List files in the given directory (vulnerable to traversal)
        files = os.listdir(path)
        return jsonify(files)
    except Exception as e:
        return jsonify([]), 400

# **4. Communicate Route Using Messages Table**
@app.route('/communicate', methods=['POST', 'GET'])
@login_required
def communicate():
    conn = get_db()
    cur = conn.cursor()
    
    # Load all existing messages from the database
    cur.execute("SELECT sender, message, response FROM messages")
    messages = cur.fetchall()
    
    # If it's a POST request, add the new message to the messages table
    if request.method == 'POST':
        message = request.form['message']

        # Insert the message into the database
        cur.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", (current_user.username, message))
        conn.commit()

        # Simulate Doc's response
        doc_reply = "Got your message, Marty!"
        cur.execute("UPDATE messages SET response = ? WHERE sender = ? AND message = ?", (doc_reply, current_user.username, message))
        conn.commit()

        conn.close()

        return redirect(url_for('communicate'))

    conn.close()
    return render_template('communicate.html', messages=messages)

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
@login_required
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



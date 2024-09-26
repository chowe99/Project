from flask import Flask, request, render_template, redirect, session, url_for, send_from_directory, abort, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import sqlite3
import os, time

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

# Manually set Doc's cookie value
DOC_SESSION_COOKIE = 'docs_cookie_value'

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
            return redirect(url_for('index'))
        else:
            return "Login failed", 401

    return render_template('login.html')

@app.route('/forgot-password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        input_username = request.form['username']

        conn = get_db()
        cur = conn.cursor()

        # Fetch all usernames from the database
        cur.execute("SELECT username FROM users")
        users = cur.fetchall()

        # Base delay of 2 seconds
        base_delay = 0.5
        max_matching_chars = 0
        valid_user = False

        # Compare input username with each stored username
        for user in users:
            stored_username = user[0]
            # Count matching characters between the input username and stored username
            matching_chars = sum(1 for x, y in zip(input_username, stored_username) if x == y)
            max_matching_chars = max(max_matching_chars, matching_chars)

            # Check if the input username is exactly the same as a stored username
            if input_username == stored_username:
                valid_user = True

        # Add delay based on the maximum number of matching characters found
        delay = base_delay + (max_matching_chars * 0.1)  # 0.1 second for each correct character
        time.sleep(delay)  # Introduce delay to simulate side-channel vulnerability

        conn.close()

        # Return different message based on whether the user is valid
        if valid_user:
            return "Password reset link sent."
        else:
            return "No such user exists.", 401

    return render_template('forgot_password.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    resp = make_response(redirect(url_for('login')))
    return resp

# **2. Directory Traversal Vulnerability Route**
@app.route('/file', methods=['POST'])
@login_required
def file():
    filename = request.form.get('filename')
    if not filename:
        return "No file selected.", 400

    # Vulnerable to directory traversal - allows user input for file paths
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return f"Contents of {filename.split('/')[-1]}:<br><pre>{content}</pre>"
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

        # Insert the message into the database (no filtering to allow XSS)
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

# **5. Secret Route Accessible Only by Doc's Cookie**
@app.route('/secret')
def secret():
    # Check if the correct 'doc_session' cookie is present
    if request.cookies.get('doc_session') == DOC_SESSION_COOKIE:
        return "This is Doc's secret page with confidential information!"
    else:
        return "Access denied!", 403

# **6. Index Route**
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Test route to manually set Doc's cookie for testing
@app.route('/set_doc_cookie')
def set_doc_cookie():
    resp = make_response("Doc's session cookie set!")
    resp.set_cookie('doc_session', DOC_SESSION_COOKIE)
    return resp

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


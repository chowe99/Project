from flask import Flask, request, render_template, redirect, session, url_for, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import os
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATABASE = '/tmp/database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome to the dashboard, {current_user.username}! <a href='/communicate'>Communicate with Doc</a>"

@app.route('/communicate', methods=['POST', 'GET'])
@login_required
def communicate():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT sender, comment FROM comments")
    comments = cur.fetchall()

    if request.method == 'POST':
        message = request.form['message']
        cur.execute("INSERT INTO comments (sender, comment) VALUES (?, ?)", (current_user.username, message))
        conn.commit()
        doc_reply = "Got your message, Marty!"
        cur.execute("INSERT INTO comments (sender, comment) VALUES (?, ?)", ("Doc", doc_reply))
        conn.commit()

        conn.close()
        return redirect(url_for('communicate'))

    conn.close()
    return render_template('communicate.html', comments=comments)

@app.route('/files/<path:filename>')
def get_file(filename):
    # Vulnerable endpoint allowing traversal to parent directories (e.g., ../flag_folder)
    base_directory = '/'
    try:
        return send_from_directory(base_directory, filename)
    except Exception as e:
        return f"Error accessing file: {e}", 404

@app.route('/secret')
def secret():
    if 'doc_session' in session and session['doc_session'] == True:
        return "This is Doc's secret page with confidential information!"
    else:
        return "Access denied!", 403

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


from flask import Flask, request, render_template, g
import sqlite3

app = Flask(__name__)

# SQLite database configuration
DATABASE = 'database.db'

def get_db():
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Example SQL Injection Vulnerability
@app.route('/user', methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        user_id = request.form['id']
        cur = get_db().cursor()
        query = f"SELECT * FROM users WHERE id = '{user_id}'"
        cur.execute(query)
        user_data = cur.fetchall()
        return render_template('user.html', user_data=user_data)
    return render_template('user.html')

# XSS Vulnerability
@app.route('/comment', methods=['POST', 'GET'])
def comment():
    if request.method == 'POST':
        user_comment = request.form['comment']
        return render_template('comment.html', user_comment=user_comment)  # Vulnerable to XSS
    return render_template('comment.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')


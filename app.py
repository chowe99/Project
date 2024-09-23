from flask import Flask, request, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# SQL Injection Vulnerability
@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        user_id = request.form['id']
        # Vulnerable query - no parameterized query, allows for SQLi
        cur = get_db().cursor()
        query = "SELECT * FROM users WHERE id = '" + user_id + "'"
        cur.execute(query)
        user_data = cur.fetchall()
        return render_template('user.html', user_data=user_data)
    return render_template('user.html')

# XSS Vulnerability
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        user_comment = request.form['comment']
        return render_template('comment.html', user_comment=user_comment)  # Vulnerable to XSS
    return render_template('comment.html')

if __name__ == "__main__":
    app.run(debug=True)


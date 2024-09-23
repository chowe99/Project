from flask import Flask, request, render_template, g
import mysql.connector
import os

app = Flask(__name__)

# MySQL database configuration from environment variables
def get_db():
    if not hasattr(g, 'db'):
        g.db = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'db'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'my-secret-pw'),
            database=os.getenv('MYSQL_DATABASE', 'hack_to_the_future')
        )
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
        query = f"SELECT * FROM users WHERE id = {user_id} OR IF(ASCII(SUBSTRING((SELECT flag FROM secrets LIMIT 1), 1, 1)) = 70, SLEEP(5), 0)"
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

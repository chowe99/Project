import subprocess
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/process_message', methods=['POST'])
def process_message():
    message = request.json.get('message')

    # Call the Node.js Puppeteer script to execute the JavaScript payload
    try:
        result = subprocess.check_output(["node", "bot.js", message], text=True)
    except Exception as e:
        result = f"Error executing script: {e}"

    return {
        'response': result,
        'doc_cookie': 'session_id=docs_session_cookie_value'
    }, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=807)


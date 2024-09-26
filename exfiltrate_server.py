from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_exfiltrated_data', methods=['POST'])
def receive_exfiltrated_data():
    data = request.json
    print(f"[Marty's Server] Received exfiltrated data: {data}")
    return "Data received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)


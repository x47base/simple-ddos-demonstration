from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello, this is your Flask API!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"data": "This is some data"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/<path:path>')
def get_flag(path):
    flag = os.getenv('FLAG', 'flag{}')
    return jsonify({"flag": flag})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9393)

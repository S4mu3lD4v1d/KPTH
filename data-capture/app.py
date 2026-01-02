from flask import Flask, request, jsonify
import redis
import json
from cryptography.fernet import Fernet
import asyncio

app = Flask(__name__)

# Simple encryption key (in prod, use env)
key = Fernet.generate_key()
cipher = Fernet(key)

r = redis.Redis(host='localhost', port=6379, db=0)

@app.route('/capture', methods=['POST'])
def capture_data():
    data = request.json
    encrypted = cipher.encrypt(json.dumps(data).encode())
    # Send to multiple destinations
    r.lpush('data_queue', encrypted)
    # Also to file or db
    with open('data.log', 'ab') as f:
        f.write(encrypted + b'\n')
    return jsonify({'status': 'captured'})

if __name__ == '__main__':
    app.run(debug=True)
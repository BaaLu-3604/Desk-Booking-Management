from flask import Flask, jsonify, request
import bcrypt
from pymongo import MongoClient


app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['login_db']
users = db['users']
users.create_index([('username', 1)], unique=True)  # Set username as a unique index

@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    data = request.json
    username = data['username']
    password = data['password']

    # Find the user in the database
    user = users.find_one({'username': username})

    if user:
        hashed_password = user['password']
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})


if __name__ == '__main__':
    app.run(debug=True,port=5003)

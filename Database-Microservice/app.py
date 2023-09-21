import random
import string
from flask import Flask, jsonify, request
import bcrypt
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['login_db']
users = db['users']
resources = db['resources']
users.create_index([('username', 1)], unique=True)  # Set username as a unique index

@app.route('/check_credentials', methods=['POST'])
def check_credentials():
    data = request.json
    username = data['username']
    password = data['password']
    # Find the user in the database
    
    user = users.find_one({'$or': [{'username': username},{'emp-id': username}]})

    if user:
        hashed_password = user['password']
        # if bcrypt.checkpw(password.encode('utf-8'), hashed_password) and password == user['emp-id']:
        #     # Redirect the user to the reset password page
        #     return jsonify({'reset_password_required': True})
        # Regular login
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            role = user.get('role', None) 
            if role:
                return jsonify({'authenticated': True, 'role': role})
    return jsonify({'authenticated': False})

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    email = data['email']
    role = data['role']

    existing_user = users.find_one({'$or': [{'username': email},{'emp_id': email}]})
    
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    random_number_string = ''.join(random.choice(string.digits) for _ in range(7))
    if role == 'Admin':
        password = "AD"+random_number_string
    if role == 'Manager':
        password = "MN"+random_number_string
    if role == 'Team Member':
        password = "TM"+random_number_string
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        'username': email,
        'emp-id': password,
        'role': role,
        'password': hashed_password
    }
    users.insert_one(user)
    
    return jsonify({"message": "User added successfully"}), 201


@app.route('/remove_user', methods=['POST'])
def remove_user():
    data = request.json
    email = data['email']
    role = data['role']

    existing_user = users.find_one({'username': email})
    
    if existing_user:
        users.delete_one({'email': email, 'role': role})
        return jsonify({"message": "User Removed successfully"}), 201
    else:
        return jsonify({"message": f"No user with username : {email}"}), 201
    


@app.route('/book_desk', methods=['POST'])
def book_desk():
    data = request.json
    email=data['Email']
    Building = data['Building']
    Select_date = data['Select_date']  
    resource = {
        'Occupied by': email,
        'Building': Building,
        'Select_date': Select_date,
    }
    resources.insert_one(resource)
    return jsonify({"message": "Booked successfully"}), 201 
if __name__ == '__main__':
    app.run(debug=True,port=5003)
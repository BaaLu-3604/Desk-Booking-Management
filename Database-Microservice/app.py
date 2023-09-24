import random,os
import string
from flask import Flask, jsonify, request, session
from pymongo import MongoClient
from bson import ObjectId 

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a strong, random secret key

client = MongoClient('mongodb://localhost:27017/')
db = client['login_db']
users = db['users']
resources = db['resources']
users.create_index([('username', 1)], unique=True)  # Set username as a unique index

@app.route('/isexists', methods=['POST'])
def isexists():
    data = request.json
    user_data = users.find_one({'$or': [{'username': data['user']}, {'emp-id': data['user']}]})
    
    if user_data:
        username = str(user_data['username'])
        role = str(user_data.get('role'))
        user_data['_id'] = str(user_data['_id'])
        return jsonify({'exists': True, 'role': role, 'user_data': username})
    return jsonify({'exists': False})

@app.route('/user_management', methods=['POST'])
def user_management():
    data = request.json
    email = data['email']
    role = data['role']

    existing_user = users.find_one({'$or': [{'username': email},{'emp_id': email}]})
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    random_number_string = ''.join(random.choice(string.digits) for _ in range(7))
    if role == 'Admin':
        emp_id = "AD"+random_number_string
    if role == 'Manager':
        emp_id = "MN"+random_number_string
    if role == 'Team Member':
        emp_id = "TM"+random_number_string

    user = {
        'username': email,
        'emp-id': emp_id,
        'role': role,
    }
    users.insert_one(user)
    
    return jsonify({"message": "User added successfully"}), 201

@app.route('/user_list', methods=['POST'])
def user_list():
    users_data = list(users.find({}))

    for user in users_data:
        user['_id'] = str(user['_id'])

    return jsonify(users_data)
    
@app.route('/remove_user', methods=['POST'])
def remove_user():
    data = request.json
    email = data.get('email')
    role = data.get('role')

    existing_user = users.find_one({'username': email, 'role': role})
    print(existing_user)
    if existing_user:
        users.delete_one({'username': email, 'role': role})
        return jsonify({"message": "User Removed successfully"}),201
    else:
        return jsonify({"message": "User not found"}),404

    
@app.route('/add_resource', methods=['POST'])
def add_resource():
    data = request.json
    building = data['building']
    block = data['block']
    desk = data['desk']
    resource = data['resources']
    data = {
        'building': building,
        'block': block,
        'desk': desk,
        'resources':resource
    }
    resources.insert_one(data)
    
    return jsonify({"message": "User added successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True,port=5004,host='0.0.0.0')

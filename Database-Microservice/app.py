from datetime import datetime
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
buildings_collection = db["buildings"]
blocks_collection = db['blocks']  # Access the existing 'blocks' collection
desks_collection = db["desks"]
users.create_index([('username', 1)], unique=True)  # Set username as a unique index
Issue_report = db['Issue_report']


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
        'empid': emp_id,
        'role': role
    }
    users.insert_one(user)
    
    return jsonify({"message": "User added successfully"}), 201

@app.route('/user_list', methods=['GET','POST'])
def user_list():
    users_data = list(users.find({}, {'_id': 0, 'username': 1,'empid':1, 'role': 1}))
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

def create_building(building_name):
    # Check if a building with the same name already exists
    building = buildings_collection.find_one({"name": building_name})
    
    if building:
        return True  # Building with the same name already exists
    else:
        building_data = {
            "name": building_name,
            "blocks": []
        }
        buildings_collection.insert_one(building_data)
        return True  # Building created successfully

# Create Operation for Blocks within a Building
def create_block(building_name, block_name):
    building = buildings_collection.find_one({"name": building_name})
    if building:
        # Check if the block already exists within the building
        block_exists = blocks_collection.find_one({"name": block_name, "building_id": building["_id"]})
        if block_exists:
            return True  # Block with the same name already exists
        else:
            block_data = {
                "name": block_name,
                "building_id": building["_id"],
                "desks": []
            }
            blocks_collection.insert_one(block_data)
            buildings_collection.update_one({"_id": building["_id"]}, {"$push": {"blocks": block_data}})
            return True  # Block created successfully
    else:
        return False  # Building not found


# Create Operation for Desks within a Block
def create_desk(block_name, desk_data):
    block = blocks_collection.find_one({"name": block_name})
    if block:
        desk_exists = desks_collection.find_one({"name": desk_data["name"], "block": block["_id"]})
        if desk_exists:
            return False  # Desk with the same name already exists in the block
        else:
            desk_data["block"] = block["_id"]
            desk_data.get("resources", []) 
            desk_data["availability"] = True  # Assuming desks are initially available
            desk_data["occupied_by"] = ""
            desk_data["date"] = datetime.now()
            desk_id = desks_collection.insert_one(desk_data).inserted_id
            blocks_collection.update_one({"_id": block["_id"]}, {"$push": {"desks": desk_id}})
            return True
    else:
        return False  # Block not found

@app.route('/add_resource', methods=['POST'])
def add_resource():
    data = request.get_json()
    building_name = data['building']
    block_name = data['block']
    desk_name = data['desk']
    resources = data['resources']
    if create_building(building_name):
        create_block(building_name, block_name)
        if create_desk(block_name, {"name": desk_name,"resources": resources}):
            return jsonify({"message": "Data added successfully!"})
        else:
            return jsonify({"error": f"Desk '{desk_name}' already exists in '{block_name}'!"})
    else:
        return jsonify({"error": f"Building '{building_name}' already exists!"})

# Route to fetch desks and their status within a block
@app.route('/get_desks_status', methods=['POST'])
def fetch_desks_status():
    data = request.get_json()
    building_name = data['Building']
    block_name = data['Block']
    
    # Check if the building exists in the database
    building = buildings_collection.find_one({"name": building_name})
    
    if building:
        # The building exists, now check the block
        block = blocks_collection.find_one({"name": block_name})
        
        if block:
            desks = desks_collection.find({"block": block["_id"]}, {"_id": 0, "name": 1, "availability": 1})
            desks_data = list(desks)
            return jsonify({"building_name": building_name, "block_name": block_name, "desks": desks_data})
        else:
            return jsonify({"error": f"No block found with name '{block_name}' in '{building_name}'."})
    else:
        return jsonify({"error": f"No building found with name '{building_name}'."})

@app.route('/issue_report', methods=['POST'])
def issue_report():
    data = request.get_json()
    Building = data['Building']
    Block=data['Block']
    Select_date = data['Date'] 
    DeskNo=data['Desk'] 
    Issue=data['Issue']

    Issue = {
        'email': session.get('username'),
        'Building': Building,
        'Block': Block,
        'Select_date': Select_date,
        'DeskNo':DeskNo,
        'Issue': Issue,
    }
    Issue_report.insert_one(Issue)
    return jsonify({"message": "successfully added your Issue"}),201
  

if __name__ == '__main__':
    app.run(debug=True,port=5004,host='0.0.0.0')
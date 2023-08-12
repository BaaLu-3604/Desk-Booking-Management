from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
client = MongoClient('mongodb://localhost:27017/')
db = client['login_db']
users = db['users']
users.create_index([('username', 1)], unique=True)  # Set username as a unique index

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password before storing it in the database.
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Save the user with the hashed password.
        user = {
            'username': username,
            'password': hashed_password
        }
        users.insert_one(user)
        
        return redirect(url_for('user_list'))

    return render_template('add-employee.html')

@app.route('/remove_user', methods=['POST'])
def remove_user():
    username = request.form['username']

    # Remove the user with the specified username.
    users.delete_one({'username': username})

    return redirect(url_for('user_list'))

@app.route('/emp-list')
def user_list():
    all_users = list(users.find())
    return render_template('emp-list.html', users=all_users)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

from flask import Flask, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    return render_template('home.html',role = session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard', username=session['username']))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd']

        response = requests.post('http://localhost:5001/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            result = response.json()

            if result['authenticated']:
                session['username'] = username
                role = result['role']
                session['role'] = role
                return redirect(url_for('dashboard', username=username,role=role))
            else:
                error = "Invalid credentials. Please try again."
                return render_template('login.html',error= error)
        else:
            error = "Error communicating with the database microservice"
            return render_template('login.html',error= error)

    return render_template('login.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))  
    return render_template('dashboard.html', username=username, role=session.get('role'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget.html')

@app.route('/add_user', methods=['GET','POST'])
def add_user():
    if session and session.get('role') != 'Admin':
        message = "You do not have permission to add users!"
        return render_template('error.html',role=session.get('role'),error= message)
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        
        response = requests.post('http://localhost:5002/add_user', json=({'email':email,'role':role}))
        if response.status_code == 200:
            message = "User Added successfully"
            return render_template('add_user.html',role=session.get('role'),error= message)

        else:
            error = "User Already exists" 
            return render_template('add.html',role=session.get('role'),error= error)
    return render_template('add_user.html',role=session.get('role'))

@app.route('/remove_user', methods=['GET','POST'])
def remove_user():
    if session and session.get('role') != 'admin':
        message = "You do not have permission to Remove users!"
        return render_template('error.html',role=session.get('role'),error= message)
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        
        response = requests.post('http://localhost:5002/remove_user', json=({'email':email,'role':role}))  
        if response.status_code == 200:
            message = "User Removed successfully"
            return render_template('remove_user.html',role=session.get('role'),error= message)
 
        else:
            error = "No User exists" 
            return render_template('remove_user.html',role=session.get('role'),error= error)
    return render_template('remove_user.html',role=session.get('role'))

@app.route('/add_resource', methods=['GET','POST'])
def add_resource():
    
    return render_template('add_resource.html',role=session.get('role'))

@app.route('/remove_resource', methods=['GET','POST'])
def remove_resource():
    return render_template('add_resource.html',role=session.get('role'))

if __name__ == '__main__':
    app.run(debug=True,port=5000)
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a strong secret key
client = MongoClient('mongodb://localhost:27017/')
db = client['login_db']
users = db['users']
users.create_index([('username', 1)], unique=True)  # Set username as a unique index

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard', username=session['username']))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve user document by username
        user = users.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username
            return redirect(url_for('dashboard', username=username))
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))  
    
    return render_template('dashboard.html', username=username)  # Render the dashboard template and pass the 'username' to display in the template


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget.html')


if __name__ == '__main__':
    app.run(debug=True)

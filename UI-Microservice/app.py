import os, requests
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_caching import Cache

load_dotenv("C:/Users/Navya/Downloads/TCS_Project/Desk-Booking-Management/UI-Microservice/ui.env")

app = Flask(__name__)
app.secret_key = os.urandom(24)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

oauth = OAuth(app)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    client_kwargs={
        'scope': 'openid email profile',
        'redirect_uri': 'http://127.0.0.1:5005/auth',
    }
)

@app.route('/home')
def home():
    return render_template('home.html', role=session.get('role'))

@app.route('/')
def index():
    return render_template('home.html', role=session.get('role'))

@app.route('/authenticate')
def authenticate():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    userinfo_response = requests.get('https://openidconnect.googleapis.com/v1/userinfo', headers={'Authorization': f'Bearer {token["access_token"]}'})
    if userinfo_response.status_code == 200:
        userinfo = userinfo_response.json()
        print(userinfo)
        user = userinfo.get('email')

        response = requests.post("http://127.0.0.1:5004/isexists", json={"user": user})
        result = response.json()
        print(response)
        if response.status_code == 200:
            if result['exists']:
                role = str(result['role'])
                username = str(result['user_data'])
                session['username'] = username
                session['role'] = role
                return redirect(url_for('dashboard'))
            else:
                return render_template('error.html', error="You did not register with this application")
        else:
            return render_template('error.html', error="You did not register with this application")
    else:
        return render_template('error.html', error="You did not with this application")

@app.route('/dashboard')
def dashboard():
    if not session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'))

@app.route('/user_management', methods=['GET','POST'])
def user_management():
    if session and session.get('role') != 'Admin':
        message = "You do not have permission to Manage Users!"
        return render_template('error.html', role=session.get('role'), error=message)
    
    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        action = request.form['action']

        if action == 'add':
            response = requests.post('http://localhost:5003/user_management', json={'email': email, 'role': role})
            if response.status_code == 200:
                return render_template('user_management.html', role=session.get('role'), user_management_error="User Added successfully")
            else:
                return render_template('user_management.html', role=session.get('role'), user_management_error="User Already Exists")
        if action == 'remove':
            response = requests.post('http://localhost:5003/remove_user', json={'email': email, 'role': role})
            print(response.status_code)
            if response.status_code == 200:
                return render_template('user_management.html', role=session.get('role'), user_management_error="User removed successfully")
            else:
                return render_template('user_management.html', role=session.get('role'), user_management_error="No User Exists")
    return render_template('user_management.html', role=session.get('role'))

@app.route('/add_resource', methods=['GET','POST'])
def add_resource():
    if session and session.get('role') != 'Admin':
        message = "You do not have permission to Add Resources!"
        return render_template('error.html', role=session.get('role'), error=message)
    if request.method == 'POST':
        building = request.form['selectBuilding']
        block = request.form['selectBlock']
        desk = request.form['deskNo']
        resources = request.form['resources']

        response = requests.post('http://localhost:5003/add_resource', json={'building': building, 'block': block, 'resources': resources, 'desk': desk})
        if response.status_code == 200:
            message = "Resource added successfully"
            return render_template('add_resource.html', role=session.get('role'), error=message)
        else:
            error = "Resource already exists"
            return render_template('add_resource.html', role=session.get('role'), error=error)
    return render_template('add_resource.html', role=session.get('role'))

@app.route('/remove_resource', methods=['GET','POST'])
def remove_resource():
    return render_template('add_resource.html', role=session.get('role'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('home')

@app.route('/book_desk', methods=['GET','POST'])
def book_desk():
    if request.method == 'POST':
        email = request.form['email']
        Building = request.form['Building']
        Select_date = request.form['datepicker']        
        response = requests.post('http://localhost:5003/book_desk', json=({'Building':Building,'Select_date':Select_date,'Email':email}))
        print(response.status_code)
        if response.status_code == 201:
            message = "Booked successfully"
            return render_template('book_desk.html',role=session.get('role'),error= message,color= 'color:green;')
        else:
            error = "unsuccessful" 
            return render_template('book_desk.html',role=session.get('role'),error= error,color= 'color:red;')
    return render_template('book_desk.html',role=session.get('role'))

@app.route('/issue_report', methods=['GET','POST'])
def issue_report():
    return render_template('book_desk.html',role=session.get('role'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)

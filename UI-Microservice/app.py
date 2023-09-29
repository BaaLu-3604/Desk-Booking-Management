import os, requests
from flask import Flask, jsonify, render_template, redirect, request, session, url_for
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask_caching import Cache


src = os.getcwd()
load_dotenv(src+"/env.env")

app = Flask(__name__)
app.secret_key = os.urandom(24)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

oauth = OAuth(app)
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
# print(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

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
        name = userinfo.get('given_name')
        response = requests.post("http://127.0.0.1:5004/isexists", json={"user": user})
        result = response.json()
        print(response)
        if response.status_code == 200:
            if result['exists']:
                role = str(result['role'])
                username = str(result['user_data'])
                session['username'] = username
                session['role'] = role
                session['name'] = name
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
    return render_template('dashboard.html', username=session.get('name'), role=session.get('role'))

@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if session and session.get('role') != 'Admin':
        message = "You do not have permission to Manage Users!"
        return render_template('error.html', role=session.get('role'), error=message)

    response = requests.post('http://localhost:5004/user_list')
    users_data = response.json()

    if request.method == 'POST':
        email = request.form['email']
        role = request.form['role']
        action = request.form['action']

        if action == 'add':
            response = requests.post('http://localhost:5003/user_management', json={'email': email, 'role': role})
            if response.status_code == 200:
                user_management_error = "User Added successfully"
            else:
                user_management_error = "User Already Exists"
        elif action == 'remove':
            response = requests.post('http://localhost:5003/remove_user', json={'email': email, 'role': role})
            if response.status_code == 200:
                user_management_error = "User removed successfully"
            else:
                user_management_error = "No User Exists"
                return render_template('user_management.html', role=session.get('role'),  user_management_error=user_management_error)
    return render_template('user_management.html', role=session.get('role'),users_data= users_data)


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
        data = {'building': building, 'block': block, 'resources': resources, 'desk': desk}
        response = requests.post('http://localhost:5003/add_resource',json=data )
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
        Building = request.form['selectBuilding']
        Block = request.form['selectBlock']
        Date = request.form['datepicker']        
        response = requests.post('http://localhost:5004/get_desks_status', json=({'Building':Building,'Block': Block,'Date': Date}))
        print(response.status_code)
        result = response.json()
        if response.status_code == 200:
            return render_template('book_desk.html', role=session.get('role'), error=response.text)
        else:
            error = "Unsuccessful: " + result.text # Display the error message from the JSON response
            return render_template('book_desk.html', role=session.get('role'), error=error)
    return render_template('book_desk.html', role=session.get('role'))

@app.route('/issue_report', methods=['GET','POST'])
def issue_report():
    if request.method == 'POST':
        Building = request.form['selectBuilding']
        Block = request.form['selectBlock']
        Date = request.form['datepicker']
        DeskNo = request.form['DeskNo']
        Issue=request.form['Issue']
        data = {'Building': Building, 'Block': Block, 'Date': Date, 'Desk': DeskNo, 'Issue': Issue}         
        response = requests.post('http://localhost:5004/issue_report', json=data)
        print(response.text)
        result = response.json()
        if response.status_code == 201:
            message = "successfully added your Issue"
            return render_template('issue_report.html', role=session.get('role'), error=message)
        else:
            error = "Unknown error"
            return render_template('issue_report.html', role=session.get('role'), error=error)
    return render_template('issue_report.html', role=session.get('role'))

app.route('/view_issues', methods=['GET','POST'])
def view_issues():
    response = requests.get('http://localhost:5004/view_issues')
    result =response.json()
    if response.status_code==200:
        return render_template('view_issues.html', username=session.get('name'), role=session.get('role'),issues=response.text)
    return render_template('view_issues.html', username=session.get('name'), role=session.get('role'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)
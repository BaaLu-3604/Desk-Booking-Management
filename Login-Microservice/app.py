import json
from flask import Flask, jsonify, render_template, redirect, session, url_for
import requests
from authlib.integrations.flask_client import OAuth
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a strong, random secret key

# Initialize OAuth with Google configuration
oauth = OAuth(app)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id='',  # Replace with your Google OAuth client ID
    client_secret='',  # Replace with your Google OAuth client secret
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/authenticate')
def authenticate():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    
    token = oauth.google.authorize_access_token()
    userinfo_response = requests.get('https://openidconnect.googleapis.com/v1/userinfo', headers={'Authorization': f'Bearer {token["access_token"]}'})

    if userinfo_response.status_code == 200:
        userinfo = userinfo_response.json()
        print(userinfo)
        user = userinfo.get('email')
        name = str(userinfo.get('name'))
        picture_url = str(userinfo.get('picture'))

        response = requests.post("http://127.0.0.1:5004/isexists",json=({"user" : user}))
        result = response.json()
        print(response)
        if response.status_code == 200:
            if result['exists']:
                role = str(result['role'])
                username = str(result['user_data'])
                # return render_template('l.html',error = result,data = userinfo,email = result['user_data'])
                return render_template('dashboard.html', user= username, role= role)
                # return jsonify({'auth' : True, 'role': role,'user': username})
            else:
                # return render_template('l.html',error = result,data = str(userinfo),email = result['user_data'])
                return render_template('home.html',error= "cant login")
            
                # return jsonify({'auth' : False})
        else:
            # return jsonify({'auth' : False})
            return render_template('home.html',error= "cant login")
            # return render_template('l.html',error = result,data = str(userinfo),email = result['user_data'])

    else:
        return jsonify({'auth' : False})

if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')

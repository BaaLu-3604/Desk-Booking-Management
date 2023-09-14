from flask import Flask, render_template, request
import requests,os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    response = requests.post('http://localhost:5004/check_credentials', json={'username': username, 'password': password})
    if response.status_code == 200:
        result = response.json()
        print(result)
        return result
    else:
        return "Error communicating with the database microservice"

@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget.html')



if __name__ == '__main__':
    app.run(debug=True,port=5002,host='0.0.0.0')

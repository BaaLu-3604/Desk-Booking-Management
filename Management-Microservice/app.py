from flask import Flask,request
import requests

app = Flask(__name__)

@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    data = request.json
    response = requests.post('http://localhost:5004/user_management', json=data)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return "Error communicating with the database microservice"

@app.route('/remove_user', methods=['POST'])
def remove_user():
    data = request.json
    response = requests.post('http://localhost:5004/remove_user', json=data)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return "Error communicating with the database microservice"

@app.route('/add_resource', methods=['GET', 'POST'])
def add_resource():
    data = request.json
    print(data)
    response = requests.post('http://localhost:5004/add_resource', json=data)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return "Error communicating with the database microservice"

if __name__ == '__main__':
    app.run(debug=True, port=5003,host='0.0.0.0')

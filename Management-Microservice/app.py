from flask import Flask,request
import requests

app = Flask(__name__)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    data = request.json
    response = requests.post('http://localhost:5003/add_user', json=data)

    if response.status_code == 200:
        result = response.json()
        return result
    else:
        return "Error communicating with the database microservice"

# @app.route('/remove_user', methods=['POST'])
# def remove_user():
#     username = request.form['username']

#     # Remove the user with the specified username.
#     users.delete_one({'username': username})

#     return redirect(url_for('user_list'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)

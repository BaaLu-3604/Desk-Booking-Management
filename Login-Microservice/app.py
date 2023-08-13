from flask import Flask, flash, render_template, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    response = requests.post('http://localhost:5003/check_credentials', json={'username': username, 'password': password})
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        flash("Error communicating with the database microservice")

@app.route('/forget', methods=['GET', 'POST'])
def forget_password():
    return render_template('forget.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    return render_template('add.html')

if __name__ == '__main__':
    app.run(debug=True,port=5001)

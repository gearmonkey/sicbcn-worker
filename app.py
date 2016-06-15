import simplejson
from flask import Flask
from firebase import firebase

conn = firebase.FirebaseApplication('https://sonar-11442.firebaseio.com', None)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users'):
def users():
    res = ""
    for user_id, data in conn.get('/users', None).items():
        res.append("<p>%s</p>"%data['username'])
    return res
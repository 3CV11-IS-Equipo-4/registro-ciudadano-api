from flask import Flask
import pymongo
from os import environ

app = Flask(__name__)

# Environmental variables config.
CONNECTION_URL = environ.get('CONNECTION_URL')
DB_NAME = environ.get('DB_NAME')
SECRET_KEY = environ.get('SECRET_KEY')

if CONNECTION_URL[0] == chr(34) and CONNECTION_URL[-1] == chr(34):
	client = pymongo.MongoClient(CONNECTION_URL[1:-1]) 
else:
	client = pymongo.MongoClient(CONNECTION_URL)

# Database connection.
try:
    database = client.get_database(DB_NAME)
except:
    database = 'Example'

# Secret key.
app.secret_key = SECRET_KEY

# Tables definition.
physical_persons_table = database.physical_persons

@app.route('/')
def welcome():
    return 'The API is online.'

if __name__ == "__main__":
    app.runt(host='0.0.0.0', port=8000, debug=True)
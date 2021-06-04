from flask import Flask
from flask_cors import CORS, cross_origin
import pymongo
from os import environ


# Flask's blueprints.
from src.moral_persons.moral_persons import build_moral_persons_blueprint
from src.physical_persons.physical_persons import build_physical_persons_blueprint

app = Flask(__name__)

# Environmental variables config.
CONNECTION_URL = environ.get('CONNECTION_URL')
DB_NAME = environ.get('DB_NAME')
SECRET_KEY = environ.get('SECRET_KEY')
GOOGLE_CLIENT_ID = environ.get('GOOGLE_CLIENT_ID')

if CONNECTION_URL[0] == chr(34) and CONNECTION_URL[-1] == chr(34):
	client = pymongo.MongoClient(CONNECTION_URL[1:-1]) 
else:
	client = pymongo.MongoClient(CONNECTION_URL)

# Database connection.
try:
    database = client.get_database(DB_NAME)
except:
    database = 'Example'

# Manejo de CORS
CORS(app, supoort_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

# Secret key.
app.secret_key = SECRET_KEY

# Tables definition.
physical_persons_table = database.physical_persons

@app.route('/')
def welcome():
    return 'The API is online.'

app.register_blueprint(build_physical_persons_blueprint(client, database, app.secret_key, GOOGLE_CLIENT_ID))
app.register_blueprint(build_moral_persons_blueprint(client, database, app.secret_key))

if __name__ == "__main__":
    app.runt(host='0.0.0.0', port=8000, debug=True)
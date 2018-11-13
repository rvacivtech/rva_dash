from configparser import ConfigParser

from flask import Flask
from flask_cors import CORS

# import config file to global object
config = ConfigParser()
config_file = './config.ini'
config.read(config_file)

# instantiate flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')

from backend.app import routes

if __name__ == '__main__':
    app.run(debug = True)
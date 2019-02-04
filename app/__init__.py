import os
from configparser import ConfigParser

from flask import Flask
from flask_cors import CORS

# print(os.getcwd())
# print(os.path.abspath('./config.ini'))

# import config file to global object
config = ConfigParser()
config_file = './config.ini'
config.read(config_file)

# instantiate flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')

from app import routes

if __name__ == '__main__':
    app.run(debug = True)


'''
run locally by executing `gunicorn rva_dash:app`

http://localhost:8000/api/parcel_summary?address=4800%20forest%20hill%20ave&zip_code=23225

http://localhost:8000/api/property_assessment?address=4800%20forest%20hill%20ave&zip_code=23225

http://localhost:8000/api/crime/count-by-neighborhood?start_date=2018-01-01&end_date=2018-06-01
'''
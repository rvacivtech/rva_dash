import json, configparser, re
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from streetaddress import StreetAddressFormatter, StreetAddressParser


# import config file to global object
config = configparser.ConfigParser()
config_file = 'config.ini'
config.read(config_file)

# instantiate flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')


def parse_street_address(street_text):
    addr_formatter = StreetAddressFormatter()
    street = addr_formatter.append_TH_to_street(street_text) 
    street = addr_formatter.abbrev_direction(street) 
    street = addr_formatter.abbrev_street_avenue_etc(street) 
    street = street.lower()
    
    addr_parser = StreetAddressParser()
    street_dict = addr_parser.parse(street)
    # street_dict['street_type'].replace('rd', 'road').replace('ln', 'lane')

    direction_regex = re.compile(r'^([nsew][nsew]?\.?\s)\w')
    try:
        direction = direction_regex.search(street_dict['street_name']).group(1)
        street_dict['street_name'] = street_dict['street_name'].replace(direction, '')
        street_dict['direction'] = direction.replace('.', '').strip()
    except:
        pass
    return street_dict 

def find_richmond_property_assessment_by_street_dict(street_dict, zip_code):
    app_token = config.get('richmond_open_data', 'app_token')
    try: 
        street_name = street_dict['street_name']
    except KeyError:
        raise KeyError('No street name found.')

    url = 'https://data.richmondgov.com/resource/jde6-giuc.json'
    payload = {
        '$$app_token': app_token,
        'street_name': street_name,
        'zip_code': zip_code,
        }
    if street_dict.get('house'):
        payload['building_number'] = street_dict.get('house')
    if street_dict.get('direction'):
        payload['street_direction'] = street_dict.get('direction')
    if street_dict.get('street_type'):
        payload['street_type'] = street_dict.get('house')

    r = requests.get(url, params=payload)
    if r.status_code != 200:
        raise Exception('Bad Response: Returned status code is {}.'.format(r.status_code))
    data = r.json()
    return data

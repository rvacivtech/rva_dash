import json, configparser, re

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from street_types import street_direction_abbreviations, street_type_abbreviations


# import config file to global object
config = configparser.ConfigParser()
config_file = 'config.ini'
config.read(config_file)

# instantiate flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = config.get('flask', 'secret_key')


def format_address_street_type(address):
    split_address = address.lower().split()
    try:
        split_address[-1] = street_type_abbreviations[split_address[-1]]
    except KeyError:
        pass
    formatted_address = ' '.join(split_address)
    return formatted_address


def format_address_direction(address):
    split_address = address.lower().split()
    try:
        split_address[1] = street_direction_abbreviations[split_address[1]]
    except KeyError:
        pass
    formatted_address = ' '.join(split_address)
    return formatted_address


def get_property_assessment_by_address(address, zip_code):
    app_token = config.get('richmond_open_data', 'app_token')
    url = 'https://data.richmondgov.com/resource/jde6-giuc.json?%24%24app_token=a3P1TkGmqcICo27FNEJlNI3yq'
    url +="&$where=lower(address)='{}'&zip_code={}".format(address.lower(), zip_code)
    
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
    data = r.json()

    if not data:
        formatted_address = format_address_street_type(address)
        url_format_1 = url.replace(address, formatted_address)
        r = requests.get(url_format_1)
        if r.status_code != 200:
            raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
        data = r.json()
        if not data:
            formatted_address = format_address_direction(format_address_street_type(address))
            url_format_2 = url.replace(address, formatted_address)
            r = requests.get(url_format_2)
            if r.status_code != 200:
                raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
            data = r.json()
    return data


def get_parcel_summary_by_address(address, zip_code):
    assessment_record = get_property_assessment_by_address(address, zip_code)
    if not assessment_record:
        raise Exception('Could not find property assessment record.  Unable to determine Parcel ID.')
    elif len(assessment_record) > 1:
        print('Warning: Provided address identified multiple assessment property records.')
    parcel_id = assessment_record[0]['pin']

    app_token = config.get('richmond_open_data', 'app_token')
    url = 'https://data.richmondgov.com/resource/hi27-ghss.json?%24%24app_token=a3P1TkGmqcICo27FNEJlNI3yq'
    url +="&$where=pin_pin='{}'".format(parcel_id)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
    data = r.json()

    if len(data) > 1:
        print('Warning: Associated Parcel ID Number (PIN) identified multiple parcel summary records.')

    return data[0]


@app.route('/', methods=['GET','POST'])
def provide_parcel_summary():
    print(request.form)
    address = request.args.get('address')
    zip_code = request.args.get('zip_code')
    data = get_parcel_summary_by_address(address, zip_code)
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
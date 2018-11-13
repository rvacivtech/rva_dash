import json, configparser, re

import requests

from backend.utilities.format_address import format_address_street_type, format_address_direction


# import config file to global object
config = configparser.ConfigParser()
config_file = 'config.ini'
config.read(config_file)


def get_property_assessment_by_address(address, zip_code):
    app_token = config.get('richmond_open_data', 'app_token')
    url = 'https://data.richmondgov.com/resource/jde6-giuc.json?%24%24app_token={}'.format(app_token)
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
            formatted_address = format_address_direction(address)
            url_format_2 = url.replace(address, formatted_address)
            r = requests.get(url_format_2)
            if r.status_code != 200:
                raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
            data = r.json()
            if not data:
                formatted_address = format_address_direction(format_address_street_type(address))
                url_format_3 = url.replace(address, formatted_address)
                r = requests.get(url_format_3)
                if r.status_code != 200:
                    raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
                data = r.json()
    return data


def get_parcel_summary_by_address(address, zip_code):
    assessment_record = get_property_assessment_by_address(address, zip_code)
    if not assessment_record:
        raise Exception('Could not find property assessment record.  Unable to determine Parcel ID.')
    elif len(assessment_record) > 1:
        print('Warning: Provided address identified multiple assessment property records.  Using first record.')
    parcel_id = assessment_record[0]['pin']

    app_token = config.get('richmond_open_data', 'app_token')
    url = 'https://data.richmondgov.com/resource/hi27-ghss.json?%24%24app_token={}'.format(app_token)
    url +="&$where=pin_pin='{}'".format(parcel_id)
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception('Bad Response: Returned status code is {}. Content: {}'.format(r.status_code, r.content))
    data = r.json()

    if len(data) > 1:
        print('Warning: Associated Parcel ID Number (PIN) identified multiple parcel summary records.')
    return data


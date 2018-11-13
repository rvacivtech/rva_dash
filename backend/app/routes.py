from flask import Flask, jsonify, request
from backend.app import app
from backend.app.api_requests import get_parcel_summary_by_address

def get_address_and_zip_from_request(request):
    if request.is_json():
        data = request.get_json()
        address = data.get('address')
        zip_code = data.get('zip_code')
    else:
        address = request.args.get('address')
        zip_code = request.args.get('zip_code')
    return (address, zip_code)

@app.route('/api/parcel_summary', methods=['GET','POST'])
def provide_parcel_summary():
    address, zip_code = get_address_and_zip_from_request(request)
    record = get_parcel_summary_by_address(address, zip_code)
    return jsonify(record)

@app.route('/api/property_assessment', methods=['GET','POST'])
def provide_property_assessment():
    address, zip_code = get_address_and_zip_from_request(request)
    record = get_parcel_summary_by_address(address, zip_code)
    return jsonify(record)

@app.route('/', methods=['GET'])
def marco():
    return 'POLO!'
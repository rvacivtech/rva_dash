import logging, datetime
from flask import Flask, jsonify, request
from app import app
from app.api_requests import get_parcel_summary_by_address, get_property_assessment_by_address
from app.models import CrimeSummary, ParcelSummary, PropertyAssessment

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('main.log')
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def get_address_and_zip_from_request(request):
    if request.is_json:
        logger.debug('JSON request received.')
        data = request.get_json()
        address = data.get('address')
        zip_code = data.get('zip_code')
    elif request.method == 'GET':
        logger.debug('GET request received.')
        address = request.args.get('address')
        zip_code = request.args.get('zip_code')
    else:
        address=None
        zip_code=None
    return (address, zip_code)

@app.route('/api/parcel_summary', methods=['GET','POST'])
def provide_parcel_summary():
    address, zip_code = get_address_and_zip_from_request(request)
    try:
        logger.debug('Attempting to get parcel summary for {} in {}.'.format(address, zip_code))
        parcel = ParcelSummary()
        record = parcel.get_parcel_summary_dict_by_address(address, zip_code)
        assert record
        msg = 'Success'
    except Exception as e:
        error_message = 'Failed to get parcel summary for {} in {}.'.format(address, zip_code)
        logger.error(error_message)
        record = ''
        msg = '{} {}'.format(error_message, e)
    logger.debug('Successfully retreived parcel summary for {} in {}.'.format(address, zip_code))
    return jsonify(msg=msg, result=record)

@app.route('/api/property_assessment', methods=['GET','POST'])
def provide_property_assessment():
    address, zip_code = get_address_and_zip_from_request(request)
    try:
        logger.debug('Attempting to get property assessment for {} in {}.'.format(address, zip_code))
        assessment = PropertyAssessment()
        record = assessment.get_property_assessment_dict_by_address(address, zip_code)
        assert record
        msg = 'Success'
    except Exception as e:
        error_message = 'Failed to get property assessment for {} in {}.'.format(address, zip_code)
        logger.error(error_message)
        record = ''
        msg = '{} {}'.format(error_message, e)
    logger.debug('Successfully retreived property assessment for {} in {}.'.format(address, zip_code))
    return jsonify(msg=msg, result=record)

@app.route('/api/crime/count-by-neighborhood', methods=['GET'])
def provide_crime_count_by_neighborhood():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    neighborhoods = request.args.getlist('neighborhood')
    parsed_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    parsed_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
    crime_summary = CrimeSummary()
    data = crime_summary.get_neighborhood_crime_count(start_date=parsed_start_date, end_date=parsed_end_date, neighborhoods=neighborhoods)
    return jsonify(result=data)


@app.route('/', methods=['GET'])
def marco():
    return 'POLO!'
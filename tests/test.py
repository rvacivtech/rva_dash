import unittest, os, re
import requests, responses
from rva_dash.utilities import format_address
from rva_dash.app import routes, api_requests

class TestUtilities(unittest.TestCase):

    def test_format_address_street_type(self):
        start_address = '1600 Pennsylvania Avenue'
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, '1600 pennsylvania ave')

        start_address = '1600 Pennsylvania Ave'
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

        start_address = '1600 Pennsylvania'
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

        start_address = ''
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

    def test_format_address_direction(self):
        start_address = '1600 North Pennsylvania Avenue'
        end_address = format_address.format_address_direction(start_address)
        self.assertEqual(end_address, '1600 n pennsylvania avenue')

        start_address = 'North 1600 Pennsylvania Ave'
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

        start_address = '1600 N. Pennsylvania Blvd.'
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

        start_address = ''
        end_address = format_address.format_address_street_type(start_address)
        self.assertEqual(end_address, start_address)

class FakeRequest():
    def __init__(self, get_json=None, args=None, response_code=200, is_json=True, method='POST'):
        self.method=method 
        self.is_json=is_json
        self.response_code=response_code
        self.args=args 
        if get_json:
            self.get_json=get_json


class TestRoutes(unittest.TestCase):

    def test_get_address_and_zip_from_request(self):
        address = "19 Main St."
        zip_code = "23225"
        address_data = {"address": address, "zip_code": zip_code}
        def get_json():
            return address_data
        
        request = FakeRequest(is_json=True, get_json=get_json)
        test_address, test_zip_code = routes.get_address_and_zip_from_request(request)
        self.assertEqual(address, test_address)
        self.assertEqual(zip_code, test_zip_code)

        request = FakeRequest(is_json=False, args=address_data, method='GET')
        test_address, test_zip_code = routes.get_address_and_zip_from_request(request)
        self.assertEqual(address, test_address)
        self.assertEqual(zip_code, test_zip_code)

        request = FakeRequest(is_json=False, args={"foo": "bar"})
        test_address, test_zip_code = routes.get_address_and_zip_from_request(request)
        self.assertIsNone(test_address)
        self.assertIsNone(test_zip_code)


class TestApiRequests(unittest.TestCase):

    @responses.activate
    def test_get_property_assessment_by_address(self):
        url_regex = re.compile(r'https://data.richmondgov.com/resource/jde6-giuc.json')
        responses.add(responses.Response(   method='GET', 
                                                url=url_regex,
                                                status=200,
                                                json=[]))
        responses.add(responses.Response(   method='GET', 
                                                url=url_regex,
                                                status=200,
                                                json=[{"foo": "bar"}]))
        address='9 N Main St.'
        zip_code='23225'
        response = api_requests.get_property_assessment_by_address(address, zip_code)
        self.assertEqual(response[0]['foo'], 'bar')

        responses.add(responses.GET, url_regex, status=500)
        self.assertRaises(Exception, api_requests.get_property_assessment_by_address(address, zip_code))


    @responses.activate
    def test_get_parcel_summary_by_address(self):
        assessment_regex = re.compile(r'https://data.richmondgov.com/resource/jde6-giuc.json')
        parcel_regex = re.compile(r'https://data.richmondgov.com/resource/hi27-ghss.json')
        responses.add(responses.Response(   method='GET', 
                                            url=assessment_regex,
                                            status=200,
                                            json=[{"pin": "1234"}]))
        responses.add(responses.Response(   method='GET', 
                                                url=parcel_regex,
                                                status=200,
                                                json=[{"foo": "bar"}]))
        
        address='9 N Main St.'
        zip_code='23225'
        response = api_requests.get_parcel_summary_by_address(address, zip_code)
        self.assertEqual(response[0]['foo'], 'bar')

        responses.add(responses.GET, parcel_regex, status=500)
        self.assertRaises(Exception, api_requests.get_parcel_summary_by_address(address, zip_code))


if __name__ == '__main__':
    unittest.main()
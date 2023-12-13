from pprint import pprint

import requests
from requests import codes

from test_api.logger import get_logs
from test_api.rest_settings import headers, base_url


class RequestApiClient:
    def __init__(self, path):
        self.path = f'{base_url}{path}'

    def _request(self, url, request_type, data=None, expected_error=False):
        stop_flag = False
        while not stop_flag:
            response = self._make_request(data, request_type, url)

            if not expected_error and response.status_code == codes.ok:
                stop_flag = True

            elif expected_error:
                stop_flag = True

        self._log_response(request_type, response)
        return response

    def _log_response(self, request_type, response):
        pprint(100 * "=")
        pprint(f'{request_type} example')
        pprint(response.url)
        pprint(response.status_code)
        pprint(response.reason)
        pprint(response.text)
        pprint(response.json())
        pprint('**********')

    def _make_request(self, data, request_type, url):
        if url.__contains__("/store/order") and request_type == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif request_type == 'GET':
            response = requests.get(url)
        elif request_type == 'POST':
            response = requests.post(url, data=data, headers=headers)
        elif request_type == 'PUT':
            response = requests.put(url, data=data, headers=headers)
        else:
            response = requests.delete(url, headers=headers)
        return response

    def get(self, path_variable, expected_error=False):
        get_url = f'{self.path}/{path_variable}'
        response = self._request(get_url, 'GET', expected_error=expected_error)
        request = response.request
        get_logs(request, response)
        return response

    def post(self, data):
        post_url = f'{self.path}'
        response = self._request(post_url, 'POST', data=data)
        request = response.request
        get_logs(request, response, data)
        return response

    def put(self, path_variable, data, expected_error=False):
        put_url = f'{self.path}/{path_variable}'
        response = self._request(put_url, 'PUT', data=data, expected_error=expected_error)
        request = response.request
        get_logs(request, response, data)
        return response

    def delete(self, username, expected_error=False):
        delete_url = f'{self.path}/{username}'
        response = self._request(delete_url, 'DELETE', expected_error=expected_error)
        request = response.request
        get_logs(request, response)
        return response

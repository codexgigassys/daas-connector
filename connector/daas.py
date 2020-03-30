import requests

from exceptions import MissingCredentialsException, InvalidCredentialsException
from utils import singleton


@singleton
class DaaS(object):
    def __init__(self, config):
        self.token = self._get_token(config['username'], config['password']) if 'token' not in config else config['token']
        self.base_url = '%s://%s:%s' % (config['protocol'], config['ip'], config['port'])
        self.callback_url = config['callback_url'] if 'callback_url' in config else None

    def _request(self, url, method, data=None):
        url = '%s/%s' % (self.base_url, url)
        return method(url, data) if data else method(url)

    def _post(self, url, data):
        return self._request(url, method=requests.post, data=data)

    def _get(self, url):
        return self._request(url, method=requests.post)

    def _get_token(self, username, password):
        if not username or not password:
            raise MissingCredentialsException()
        response = self._post('api/get_token/', {'username': username, 'password': password})
        if response.status_code != 200:
            raise InvalidCredentialsException()
        return response.json()['token']

    def _check_status_code(self, method_name, real_status_code, expected_status_code):
        error_message = 'status code of DaaS(...).%s(...) should be %s, but it is %s.' % (method_name, expected_status_code, real_status_code)
        assert real_status_code == expected_status_code, error_message

    def download_source_code(self, daas_sample_id):
        response = self._get('api/download_source_code/%s/' % daas_sample_id).content
        self._check_status_code('download_source_code', response.status_code, 200)
        return response

    def send_sample_url(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        data = {'file_url': file_url,
                'file_name': file_name,
                'zip_password': zip_password,
                'force_reprocess': force_reprocess}
        if self.callback_url:
            data['callback'] = self.callback_url
        response = self._post('api/upload/', data)
        self._check_status_code('send_sample_url', response.status_code, 202)
        return response

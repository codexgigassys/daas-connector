import requests
import socket

from env import envget
from exceptions import MissingCredentialsException, InvalidCredentialsException
from utils import singleton


@singleton
class DaaS(object):
    def __init__(self):
        self.token = self._get_token(envget('daas.credentials.username'), envget('daas.credentials.password'))
        self.base_url = self._build_base_url('api')
        callback_base_url = self._build_base_url('callback')
        callback_path = envget('daas.callback.path')
        self.callback_url = '%s/%s' % (callback_base_url, callback_path)

    def _build_base_url(self, prefix):
        callback_protocol = envget('daas.%s.protocol' % prefix)
        # Get the IP to not use a host with underscores and avoid django raising RFC errors.
        callback_ip = socket.gethostbyname(envget('daas.%s.domain' % prefix))
        callback_port = envget('daas.%s.port' % prefix)
        return '%s://%s:%s' % (callback_protocol, callback_ip, callback_port)

    def _request(self, url, method, data=None):
        url = '%s/%s' % (self.base_url, url)
        return method(url, json=data, verify=False) if data else method(url, verify=False)

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

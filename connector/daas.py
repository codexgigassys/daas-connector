import pathmagic
import requests
import socket
import logging

from exceptions import UnexpectedDaaSResponseException
from utils import singleton
# Try to import envget from codex
try:
    from env import envget
except ImportError:
    raise Exception('Create an "envget" function inside an "env" file to load configuration')


@singleton
class DaaS(object):
    def __init__(self):
        # Build URLs
        self.base_url = self._build_base_url('api')
        callback_base_url = self._build_base_url('callback')
        callback_path = envget('daas.callback.path')
        self.callback_url = '%s/%s' % (callback_base_url, callback_path)
        # Get token
        self.token = envget('daas.credentials.token')
        # This is parametrized to allow dependency injection. We can not do it at __init__'s parameter level because
        # this is a singleton.
        self._requests_library = requests

    def _build_base_url(self, prefix):
        callback_protocol = envget('daas.%s.protocol' % prefix)
        # Get the IP to not use a host with underscores and avoid django raising RFC errors.
        callback_ip = socket.gethostbyname(envget('daas.%s.domain' % prefix))
        callback_port = envget('daas.%s.port' % prefix)
        return '%s://%s:%s' % (callback_protocol, callback_ip, callback_port)

    def _request(self, url, method, data=None, expected_status_code=None):
        url = '%s/%s' % (self.base_url, url)
        response = method(url, json=data, verify=False) if data else method(url, verify=False)
        if expected_status_code:
            error_message = 'requests.%s(%s, json=%s) status code is %s, while expected status code is %s'\
                            % (method.__name__, url, data, response.status_code, expected_status_code)
            assert response.status_code == expected_status_code, error_message
        return response

    def _post(self, url, **kwargs):
        return self._request(url, method=self._requests_library.post, **kwargs)

    def _get(self, url, **kwargs):
        return self._request(url, method=self._requests_library.get, **kwargs)

    def download_source_code(self, sample_sha1):
        return self._get('api/download_source_code/%s' % sample_sha1, expected_status_code=200).content

    def send_sample_url(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        data = {'file_url': file_url,
                'file_name': file_name,
                'zip_password': zip_password,
                'force_reprocess': force_reprocess}
        if self.callback_url:
            data['callback'] = self.callback_url
        return self._post('api/upload', data=data, expected_status_code=202)

    def has_sample(self, hash):
        response = self._get('api/get_sample_from_hash/%s' % hash)
        if response.status_code == 200:
            uploaded_to_daas = True
        elif response.status_code == 404:
            uploaded_to_daas = False
        else:
            raise UnexpectedDaaSResponseException()
        return uploaded_to_daas

    def sample_was_decompiled(self, hash):
        response = self._get('api/get_sample_from_hash/%s' % hash)
        logging.error('sample_was_decompiled(): response.status_code=%s  &  response.json()=%s' %
                      (response.status_code, response.content))
        if response.status_code == 200:
            decompiled = response.json()['decompiled'] if 'decompiled' in response.json() else False
        elif response.status_code == 404:
            decompiled = False
        else:
            raise UnexpectedDaaSResponseException()
        return decompiled

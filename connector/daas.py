import pathmagic
import requests
import socket
import logging

from env import envget
from exceptions import MissingCredentialsException, InvalidCredentialsException, UnexpectedDaaSResponseException
from utils import singleton


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
        return self._request(url, method=requests.get)

    def _check_status_code(self, method_name, real_status_code, expected_status_code):
        error_message = 'status code of DaaS(...).%s(...) should be %s, but it is %s.' % (method_name, expected_status_code, real_status_code)
        assert real_status_code == expected_status_code, error_message

    def download_source_code(self, sample_sha1):
        response = self._get('api/download_source_code/%s' % sample_sha1)
        self._check_status_code('download_source_code', response.status_code, 200)
        return response.content

    def send_sample_url(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        data = {'file_url': file_url,
                'file_name': file_name,
                'zip_password': zip_password,
                'force_reprocess': force_reprocess}
        if self.callback_url:
            data['callback'] = self.callback_url
        response = self._post('api/upload', data)
        self._check_status_code('send_sample_url', response.status_code, 202)
        return response

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

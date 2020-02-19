import requests

import config
from exceptions import MissingCredentialsException, InvalidCredentialsException
from utils import ThreadSafeSingleton


class DaaS(metaclass=ThreadSafeSingleton):
    def __init__(self):
        self._token = config.TOKEN

    @property
    def base_url(self):
        return '%s://%s:%s' % (config.PROTOCOL, config.IP, config.PORT)

    @property
    def token(self):
        if not self._token:
            self._token = self._get_token()
        return self._token

    def _request(self, url, method, data=None):
        url = '%s/%s' % (self.base_url, url)
        return method(url, data) if data else method(url)

    def _post(self, url, data):
        return self._request(url, method=requests.post, data=data)

    def _get(self, url):
        return self._request(url, method=requests.post)

    def _get_token(self):
        if not config.USERNAME or not config.PASSWORD:
            raise MissingCredentialsException()
        response = self._post('api/get_token/', {'username': config.USERNAME, 'password': config.PASSWORD})
        if response.status_code != 200:
            raise InvalidCredentialsException()
        return response.json()['token']

    def download_source_code(self, daas_sample_id):
        return self._get('api/download_source_code/%s/' % daas_sample_id).content

    def upload_sample(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        data = {'file_url': file_url,
                'file_name': file_name,
                'zip_password': zip_password,
                'force_reprocess': force_reprocess}
        if config.CALLBACK_URL:
            data['callback'] = config.CALLBACK_URL
        response = self._post('api/upload/', data)
        assert response.status_code == 202
        return response

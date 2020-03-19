import requests

from exceptions import MissingCredentialsException, InvalidCredentialsException
from utils import ThreadSafeSingleton


class DaaS(object):
    __metaclass__ = ThreadSafeSingleton

    def __init__(self, config):
        self.token = self._get_token(config['username'], config['password']) if not config['token'] else config['token']
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

    def download_source_code(self, daas_sample_id):
        return self._get('api/download_source_code/%s/' % daas_sample_id).content

    def send_sample_url(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        data = {'file_url': file_url,
                'file_name': file_name,
                'zip_password': zip_password,
                'force_reprocess': force_reprocess}
        if self.callback_url:
            data['callback'] = self.callback_url
        response = self._post('api/upload/', data)
        assert response.status_code == 202
        return response

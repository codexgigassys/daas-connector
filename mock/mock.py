import requests

from response_mock import ResponseMock
from connector.utils import singleton


@singleton
class DaaSMock(object):
    def __index__(self, config):
        self.mocked_responses = {}
        self.callback_url = config['callback_url'] if 'callback_url' in config else None

    """ Mocked methods """
    def download_source_code(self, daas_sample_id):
        return self.mocked_responses[daas_sample_id]['source_code']

    def send_sample_url(self, file_url, file_name, zip_password='codex', force_reprocess=False):
        return ResponseMock(202)

    """ Mock configurations and management methods """
    def add_mocked_response(self, daas_sample_id, file_name, source_code, triggers_callback=True):
        """ set daas_sample_id to download the source code and file_name to trigger callbacks """
        mocked_response = {'daas_sample_id': daas_sample_id,
                           'source_code': source_code,
                           'triggers_callback': triggers_callback}
        self.mocked_responses[daas_sample_id] = mocked_response
        self.mocked_responses[file_name] = mocked_response

    def trigger_callback(self, file_name):
        if self.mocked_responses[file_name]['triggers_callback']:
            requests.post(self.callback_url, {'id': self.mocked_responses[file_name]['daas_sample_id']})

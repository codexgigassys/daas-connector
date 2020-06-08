import requests
import json

# We use global variables so this class acts a singleton without braking the library interface.
# You can modify values. To do reall callbacks, just use the normal request library instead of the mock,
# instead of setting the expected values for the following variables
_has_sample_status_code = 404  # This will force codex to upload the sample and wait for the callback.
_has_sample_message = json.dumps({'message': 'Sample dos not exist'})  # To also get the real response that DaaS returns over a 404.


def get(url, *args, **kwargs):
    response = requests.get(url, *args, **kwargs)
    if url.find('api/get_sample_from_hash') >= 0:
        response.status_code = _has_sample_status_code
        response._content = _has_sample_message  # to override response.content, response.json() and so on
    return response


def post(*args, **kwargs):
    return requests.post(*args, **kwargs)


def set_has_sample_status_code(value):
    global _has_sample_status_code
    _has_sample_status_code = value


def set_has_sample_message(message):
    global _has_sample_message
    _has_sample_message = json.dumps(message)


def reset():
    set_has_sample_status_code(404)
    set_has_sample_message({'message': 'Sample dos not exist'})

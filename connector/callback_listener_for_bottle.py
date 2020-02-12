from bottle import route
from bottle import request

import config


@route(config.CALLBACK_URL, method='POST')
def callback_listener():
    """ Method for Bottle web framework to listen to callbacks.
        Just import this function into your bottle main file to use it. """
    sample_sha1 = request.forms.get('sha1')
    daas_sample_id = request.forms.get('id')
    is_decompilable = int(request.forms.get('result').get('exit_status')) == 0
    config.PROCESS_CALLBACK_FUNCTION(sample_sha1, is_decompilable, daas_sample_id)

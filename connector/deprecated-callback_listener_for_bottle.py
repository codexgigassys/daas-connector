from bottle import request


def callback_listener(process_callback_function):
    """ Function for Bottle web framework to listen to callbacks.
        To use this fuction, create a new function with the following decorator:
        @route(config.CALLBACK_URL, method='POST')
        and call this function inside the new one.
        The first argument should be a function that receives a sha1 (str), a boolean and an integer.
        The return is optional. """
    sample_sha1 = request.forms.get('sha1')
    daas_sample_id = request.forms.get('id')
    is_decompilable = int(request.forms.get('result').get('exit_status')) == 0
    return process_callback_function(sample_sha1, is_decompilable, daas_sample_id)

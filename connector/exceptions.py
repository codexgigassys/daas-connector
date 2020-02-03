class MissingCredentialsException(Exception):
    def __init__(self, msg='You need to either set TOKEN or USERNAME + PASSWORD at config.py', *args, **kwargs):
        super(Exception, self).__init__(msg, *args, **kwargs)


class InvalidCredentialsException(Exception):
    def __init__(self, msg='Username or password is invalid.', *args, **kwargs):
        super(Exception, self).__init__(msg, *args, **kwargs)

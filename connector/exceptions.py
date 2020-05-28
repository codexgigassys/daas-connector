class UnexpectedDaaSResponseException(Exception):
    def __init__(self, msg='Expected status code differs from the received one.', *args, **kwargs):
        super(Exception, self).__init__(msg, *args, **kwargs)

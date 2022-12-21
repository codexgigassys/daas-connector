class DaaSException(Exception):
    pass


class DaaSResponseException(DaaSException):
    pass


class DaaSRequestException(DaaSException):
    pass


class DaaSNotFoundError(DaaSResponseException):
    pass

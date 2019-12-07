class APIError(Exception):
    def __init__(self, message, response, *args):
        self.response = response
        super().__init__(message, *args)


class InvalidRequestError(APIError):
    pass


class IncorrectResponseError(APIError):
    pass


class InvalidAccessTokenError(APIError):
    pass


class AccessTokenExpiredError(APIError):
    pass


class PermissionDeniedError(APIError):
    pass

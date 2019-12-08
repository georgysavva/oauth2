class APIError(Exception):
    def __init__(self, message, response, *args):
        self.response = response
        super().__init__(message, *args)


class InvalidRequestError(APIError):
    pass


class IncorrectResponseError(APIError):
    pass


class ResourceAuthorizationError(APIError):
    pass


class InvalidAccessTokenError(ResourceAuthorizationError):
    pass


class AccessTokenExpiredError(ResourceAuthorizationError):
    pass


class PermissionDeniedError(ResourceAuthorizationError):
    pass

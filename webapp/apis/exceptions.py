class APIError(Exception):
    pass


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

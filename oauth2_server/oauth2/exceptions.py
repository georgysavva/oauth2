class OAuthError(Exception):
    pass


class UnsupportedGrantTypeError(OAuthError):
    pass


class InvalidClientError(OAuthError):
    pass


class InvalidAccessTokenError(OAuthError):
    def __init__(self, *args):
        args = args or ('Access token is invalid',)
        super().__init__(*args)


class ExpiredAccessTokenError(OAuthError):
    pass

class OAuthError(Exception):
    pass


class UnsupportedGrantTypeError(OAuthError):
    pass


class InvalidClientError(OAuthError):
    pass

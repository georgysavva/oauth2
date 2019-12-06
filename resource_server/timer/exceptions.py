class PermissionDeniedError(Exception):
    def __init__(self, message, denied_resource, *args):
        self.denied_resource = denied_resource
        super().__init__(message, *args)

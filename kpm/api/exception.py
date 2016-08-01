class ApiException(Exception):
    status_code = 500
    errorcode = "internal-error"

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.payload = dict(payload or ())
        self.message = message

    def to_dict(self):
        r = {"code": self.errorcode,
             "message": self.message,
             "details": self.payload}
        return r


class InvalidUsage(ApiException):
    status_code = 400
    errorcode = "invalid-usage"


class InvalidVersion(ApiException):
    status_code = 422
    errorcode = "invalid-version"


class PackageAlreadyExists(ApiException):
    status_code = 409
    errorcode = "package-exists"


class PackageNotFound(ApiException):
    status_code = 404
    errorcode = "package-not-found"


class PackageVersionNotFound(ApiException):
    status_code = 404
    errorcode = "package-version-not-found"

# https://developer.tastytrade.com/api-overview/#api-overview - Error Codes


class InvalidRequestError(Exception):
    """Exception raised for invalid requests to the API."""

    code = 400

    def __init__(self, message):
        self.message = f"Code: {self.code} -  Invalid request from API (probably invalid parameters) {message}"
        super().__init__(self.message)


class AuthorizationExpiredError(Exception):
    """Exception raised for expired authorization."""

    code = 401

    def __init__(self, message):
        self.message = f"Code: {self.code} -  Authorization expired (try logging in again) {message}"
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """Exception raised for unauthorized access."""

    code = 403

    def __init__(self, message):
        self.message = f"Code: {self.code} -  Unauthorized access (might be accessing the wrong account with the wrong customer) {message}"
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exception raised for not found errors."""

    code = 404

    def __init__(self, message):
        self.message = f"Code: {self.code} -  Not found (data may not exist) {message}"
        super().__init__(self.message)


class UnprocessableContentError(Exception):
    """Exception raised for unprocessable content errors."""

    code = 422

    def __init__(self, message):
        self.message = f"Code: {self.code} -  Unprocessable content (invalid action performed) {message}"
        super().__init__(self.message)


class TooManyRequestsError(Exception):
    """Exception raised for too many requests."""

    code = 429

    def __init__(self, message):
        self.message = (
            f"Code: {self.code} -  Too many requests (rate limit exceeded) {message}"
        )
        super().__init__(self.message)


class InternalServerError(Exception):
    """Exception raised for internal server errors."""

    code = 500

    def __init__(self, message):
        self.message = (
            f"Code: {self.code} -  Internal server error (try again later) {message}"
        )
        super().__init__(self.message)


def translate_error_code(code: int, message: str) -> Exception:
    """
    Translate error codes to exceptions.
    """
    if code == 400:
        return InvalidRequestError(message)
    elif code == 401:
        return AuthorizationExpiredError(message)
    elif code == 403:
        return UnauthorizedError(message)
    elif code == 404:
        return NotFoundError(message)
    elif code == 422:
        return UnprocessableContentError(message)
    elif code == 429:
        return TooManyRequestsError(message)
    elif code == 500:
        return InternalServerError(message)
    else:
        return Exception(f"Unknown error: {message}")

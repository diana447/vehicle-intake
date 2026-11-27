from http import HTTPStatus


class ApplicationError(Exception):
    status_code = HTTPStatus.BAD_REQUEST
    default_code = "application_error"

    def __init__(self, detail: str, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        self.code = code or self.default_code


class AuthenticationError(ApplicationError):
    status_code = HTTPStatus.UNAUTHORIZED
    default_code = "authentication_error"


class NotFoundError(ApplicationError):
    status_code = HTTPStatus.NOT_FOUND
    default_code = "not_found"


class ServiceUnavailableError(ApplicationError):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    default_code = "service_unavailable"


class ConflictError(ApplicationError):
    status_code = HTTPStatus.CONFLICT
    default_code = "conflict"

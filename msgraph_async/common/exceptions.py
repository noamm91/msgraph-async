from http import HTTPStatus


class GraphClientException(Exception):

    def __init__(self, message):
        self.message = message


class BaseHttpError(Exception):

    def __init__(self, status, request_url, response_content, response_headers):
        Exception.__init__(self)
        self.status = status
        self.request_url = request_url
        self.response_content = response_content
        self.response_headers = response_headers

    def __str__(self):
        return f"request url: {self.request_url}, status: {self.status},  response: {str(self.response_content)}"


class UnknownError(BaseHttpError):
    pass


class BadRequest(BaseHttpError):
    pass


class Unauthorized(BaseHttpError):
    pass


class Forbidden(BaseHttpError):
    pass


class NotFound(BaseHttpError):
    pass


class MethodNotAllowed(BaseHttpError):
    pass


class NotAcceptable(BaseHttpError):
    pass


class Conflict(BaseHttpError):
    pass


class Gone(BaseHttpError):
    pass


class LengthRequired(BaseHttpError):
    pass


class PreconditionFailed(BaseHttpError):
    pass


class RequestEntityTooLarge(BaseHttpError):
    pass


class UnsupportedMediaType(BaseHttpError):
    pass


class RequestedRangeNotSatisfiable(BaseHttpError):
    pass


class UnprocessableEntity(BaseHttpError):
    pass


class TooManyRequests(BaseHttpError):
    pass


class InternalServerError(BaseHttpError):
    pass


class NotImplemented(BaseHttpError):
    pass


class ServiceUnavailable(BaseHttpError):
    pass


class GatewayTimeout(BaseHttpError):
    pass


class InsufficientStorage(BaseHttpError):
    pass


status2exception = {
    HTTPStatus.UNAUTHORIZED: Unauthorized,
    HTTPStatus.BAD_REQUEST: BadRequest,
    HTTPStatus.FORBIDDEN: Forbidden,
    HTTPStatus.NOT_FOUND: NotFound,
    HTTPStatus.METHOD_NOT_ALLOWED: MethodNotAllowed,
    HTTPStatus.NOT_ACCEPTABLE: NotAcceptable,
    HTTPStatus.CONFLICT: Conflict,
    HTTPStatus.GONE: Gone,
    HTTPStatus.LENGTH_REQUIRED: LengthRequired,
    HTTPStatus.PRECONDITION_FAILED: PreconditionFailed,
    HTTPStatus.REQUEST_ENTITY_TOO_LARGE: RequestEntityTooLarge,
    HTTPStatus.UNSUPPORTED_MEDIA_TYPE: UnsupportedMediaType,
    HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE: RequestedRangeNotSatisfiable,
    HTTPStatus.UNPROCESSABLE_ENTITY: UnprocessableEntity,
    HTTPStatus.TOO_MANY_REQUESTS: TooManyRequests,
    HTTPStatus.INTERNAL_SERVER_ERROR: InternalServerError,
    HTTPStatus.NOT_IMPLEMENTED: NotImplemented,
    HTTPStatus.SERVICE_UNAVAILABLE: ServiceUnavailable,
    HTTPStatus.GATEWAY_TIMEOUT: GatewayTimeout,
    HTTPStatus.INSUFFICIENT_STORAGE: InsufficientStorage,
}
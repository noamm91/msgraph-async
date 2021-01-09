from http import HTTPStatus


class BaseError(Exception):
    pass


class GraphClientException(BaseError):
    pass


class UnknownError(BaseError):
    pass

class BadRequest(BaseError):
    pass


class Unauthorized(BaseError):
    pass


class Forbidden(BaseError):
    pass


class NotFound(BaseError):
    pass


class MethodNotAllowed(BaseError):
    pass


class NotAcceptable(BaseError):
    pass


class Conflict(BaseError):
    pass


class Gone(BaseError):
    pass


class LengthRequired(BaseError):
    pass


class PreconditionFailed(BaseError):
    pass


class RequestEntityTooLarge(BaseError):
    pass


class UnsupportedMediaType(BaseError):
    pass


class RequestedRangeNotSatisfiable(BaseError):
    pass


class UnprocessableEntity(BaseError):
    pass


class TooManyRequests(BaseError):

    def __init__(self, *args, **kwargs):
        BaseError.__init__(self)
        print("TooManyRequests")


class InternalServerError(BaseError):
    pass


class NotImplemented(BaseError):
    pass


class ServiceUnavailable(BaseError):
    pass


class GatewayTimeout(BaseError):
    pass


class InsufficientStorage(BaseError):
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
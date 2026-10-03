"""Exception taxonomy for the Rentman API client."""


class RentmanError(Exception):
    """Base class for every error this library raises."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class RentmanCommunicationError(RentmanError):
    """The Rentman API answered with an unexpected failure or could not be reached."""


class RentmanTimeoutError(RentmanCommunicationError):
    """A Rentman request exceeded the configured timeout."""


class RentmanInvalidResponseError(RentmanCommunicationError):
    """A response carried an unusable payload, such as malformed JSON."""


class RentmanNotFoundError(RentmanCommunicationError):
    """A requested object does not exist."""


class RentmanAuthenticationError(RentmanError):
    """The API token is missing or was rejected."""


class RentmanValidationError(RentmanError):
    """The Rentman API rejected a request body or query as invalid."""


class RentmanAuthorizationError(RentmanError):
    """The token does not grant access to this resource."""


class RentmanRateLimitError(RentmanError):
    """The request exceeded the Rentman rate limits.

    Rentman allows 10 requests per second, at most 20 concurrent requests,
    and 50.000 requests per day. The client paces its own requests, so this
    error usually means another consumer of the same account is spending the
    shared budget. ``retry_after`` holds the Retry-After delay in seconds
    when the response provides one.
    """

    def __init__(
        self,
        message: str,
        status: int | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status)
        self.retry_after = retry_after


class RentmanClientClosedError(RentmanError):
    """The client was closed, so no further requests can be made."""

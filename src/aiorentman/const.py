"""Wire constants for the Rentman API."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

BASE_URL = "https://api.rentman.net"

TOKEN_ENV_VAR = "RENTMAN_TOKEN"  # noqa: S105

OAS_VERSION = "1.16.0"

DEFAULT_REQUEST_TIMEOUT = 30.0
DEFAULT_REQUESTS_PER_SECOND = 10.0
DEFAULT_MAX_CONCURRENT_REQUESTS = 20

MAX_PAGE_LIMIT = 1500

try:
    USER_AGENT = f"aiorentman/{_version('aiorentman')}"
except PackageNotFoundError:
    USER_AGENT = "aiorentman/0.0.0"

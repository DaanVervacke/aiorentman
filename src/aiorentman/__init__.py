"""Public API for aiorentman."""

import importlib.metadata

from .client import RentmanClient
from .exceptions import (
    RentmanAuthenticationError,
    RentmanAuthorizationError,
    RentmanClientClosedError,
    RentmanCommunicationError,
    RentmanError,
    RentmanInvalidResponseError,
    RentmanNotFoundError,
    RentmanRateLimitError,
    RentmanTimeoutError,
)
from .models import (
    Accessory,
    ActualContent,
    Alternative,
    Equipment,
    EquipmentAssignedSerial,
    EquipmentSetContent,
    ExtraInputField,
    Folder,
    Project,
    ProjectEquipment,
    RentmanLink,
    RentmanPage,
    Repair,
    SerialNumber,
    Status,
    StockLocation,
    StockMovement,
    Subproject,
    Supplier,
    Vehicle,
    WarehouseStatus,
)
from .query import (
    Query,
    Sort,
    eq,
    gt,
    gte,
    is_null,
    lt,
    lte,
    neq,
)

try:
    __version__ = importlib.metadata.version("aiorentman")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "Accessory",
    "ActualContent",
    "Alternative",
    "Equipment",
    "EquipmentAssignedSerial",
    "EquipmentSetContent",
    "ExtraInputField",
    "Folder",
    "Project",
    "ProjectEquipment",
    "Query",
    "RentmanAuthenticationError",
    "RentmanAuthorizationError",
    "RentmanClient",
    "RentmanClientClosedError",
    "RentmanCommunicationError",
    "RentmanError",
    "RentmanInvalidResponseError",
    "RentmanLink",
    "RentmanNotFoundError",
    "RentmanPage",
    "RentmanRateLimitError",
    "RentmanTimeoutError",
    "Repair",
    "SerialNumber",
    "Sort",
    "Status",
    "StockLocation",
    "StockMovement",
    "Subproject",
    "Supplier",
    "Vehicle",
    "WarehouseStatus",
    "__version__",
    "eq",
    "gt",
    "gte",
    "is_null",
    "lt",
    "lte",
    "neq",
]

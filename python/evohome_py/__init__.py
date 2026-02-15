"""
MyTotalConnectComfort API Client

A Python client library for the MyTotalConnectComfort (Honeywell Evohome) API.
"""

from .client import Client
from .models import Zone, Location, UserInfo, Gateway
from .exceptions import (
    MyTotalConnectComfortError,
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
    SessionExpiredError,
)
from .config import Config

__version__ = "0.2.2"

__all__ = [
    "Client",
    "Zone",
    "Location",
    "UserInfo",
    "Gateway",
    "Config",
    "MyTotalConnectComfortError",
    "AuthenticationError",
    "APIError",
    "ZoneNotFoundError",
    "LocationNotFoundError",
    "SessionExpiredError",
]

"""
MyTotalConnectComfort API Client

A Python client library for the MyTotalConnectComfort (Honeywell Evohome) API.
"""

from .client import Client
from .exceptions import (
    MyTotalConnectComfortError,
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
)
from .models import Zone, Location, UserInfo, Gateway

__version__ = "0.1.0"
__all__ = [
    "Client",
    "MyTotalConnectComfortError",
    "AuthenticationError",
    "APIError",
    "ZoneNotFoundError",
    "LocationNotFoundError",
    "Zone",
    "Location",
    "UserInfo",
    "Gateway",
]

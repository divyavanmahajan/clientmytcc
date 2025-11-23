"""
Custom exceptions for the MyTotalConnectComfort API client.
"""


class MyTotalConnectComfortError(Exception):
    """Base exception for all MyTotalConnectComfort errors."""
    pass


class AuthenticationError(MyTotalConnectComfortError):
    """Raised when authentication fails."""
    pass


class APIError(MyTotalConnectComfortError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ZoneNotFoundError(MyTotalConnectComfortError):
    """Raised when a requested zone is not found."""
    pass


class LocationNotFoundError(MyTotalConnectComfortError):
    """Raised when a requested location is not found."""
    pass


class SessionExpiredError(MyTotalConnectComfortError):
    """Raised when the session has expired and needs to be refreshed."""
    pass

"""Tests for custom exceptions."""

import pytest
from mytotalconnectcomfort.exceptions import (
    MyTotalConnectComfortError,
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
    SessionExpiredError,
)


class TestExceptionHierarchy:
    """Test exception hierarchy."""

    def test_base_exception(self):
        """Test base exception."""
        exc = MyTotalConnectComfortError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError("Invalid credentials")
        assert str(exc) == "Invalid credentials"
        assert isinstance(exc, MyTotalConnectComfortError)

    def test_api_error(self):
        """Test APIError."""
        exc = APIError("API failed", status_code=500, response={"error": "Internal"})
        assert str(exc) == "API failed"
        assert exc.status_code == 500
        assert exc.response == {"error": "Internal"}
        assert isinstance(exc, MyTotalConnectComfortError)

    def test_api_error_without_details(self):
        """Test APIError without status code and response."""
        exc = APIError("API failed")
        assert str(exc) == "API failed"
        assert exc.status_code is None
        assert exc.response is None

    def test_zone_not_found_error(self):
        """Test ZoneNotFoundError."""
        exc = ZoneNotFoundError("Zone 123 not found")
        assert str(exc) == "Zone 123 not found"
        assert isinstance(exc, MyTotalConnectComfortError)

    def test_location_not_found_error(self):
        """Test LocationNotFoundError."""
        exc = LocationNotFoundError("Location 456 not found")
        assert str(exc) == "Location 456 not found"
        assert isinstance(exc, MyTotalConnectComfortError)

    def test_session_expired_error(self):
        """Test SessionExpiredError."""
        exc = SessionExpiredError("Session has expired")
        assert str(exc) == "Session has expired"
        assert isinstance(exc, MyTotalConnectComfortError)


class TestExceptionCatching:
    """Test catching exceptions."""

    def test_catch_specific_exception(self):
        """Test catching specific exception."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Test")

    def test_catch_base_exception(self):
        """Test catching base exception catches all."""
        with pytest.raises(MyTotalConnectComfortError):
            raise ZoneNotFoundError("Test")

        with pytest.raises(MyTotalConnectComfortError):
            raise AuthenticationError("Test")

        with pytest.raises(MyTotalConnectComfortError):
            raise APIError("Test")

    def test_exception_message_matching(self):
        """Test exception message matching."""
        with pytest.raises(AuthenticationError, match="Invalid"):
            raise AuthenticationError("Invalid credentials")

        with pytest.raises(ZoneNotFoundError, match="Zone.*not found"):
            raise ZoneNotFoundError("Zone 123 not found")

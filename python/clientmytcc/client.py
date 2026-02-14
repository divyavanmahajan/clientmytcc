"""
Main client for the MyTotalConnectComfort API.
"""

import re
from typing import List, Optional, Dict, Any
import requests

from .models import Location, Zone, UserInfo
from .exceptions import (
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
    SessionExpiredError,
)


class Client:
    """
    Client for interacting with the MyTotalConnectComfort API.
    
    Example:
        >>> client = Client()
        >>> client.login("user@example.com", "password")
        >>> locations = client.get_locations()
        >>> for location in locations:
        ...     print(f"{location.name}: {len(location.zones)} zones")
    """
    
    BASE_URL = "https://international.mytotalconnectcomfort.com"
    
    def __init__(self, cookies: Optional[Dict[str, str]] = None):
        """
        Initialize the client with a requests session.
        
        Args:
            cookies: Optional dictionary of cookies to initialize the session with
        """
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
        })
        
        if cookies:
            self.session.cookies.update(cookies)
            self._authenticated = True
        else:
            self._authenticated = False
            
        self._csrf_token: Optional[str] = None
        self._anti_forgery_token: Optional[str] = None
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with the MyTotalConnectComfort API.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Login response data containing user information
            
        Raises:
            AuthenticationError: If login fails
            APIError: If the API returns an error
        """
        # First, get the login page to obtain CSRF tokens
        login_page_url = f"{self.BASE_URL}/Account/Login"
        response = self.session.get(login_page_url)
        response.raise_for_status()
        
        # Extract CSRF token from cookies
        self._csrf_token = self.session.cookies.get("__RequestVerificationToken")
        
        # Extract anti-forgery token from page content
        self._extract_anti_forgery_token(response.text)
        
        # Prepare login request
        login_url = f"{self.BASE_URL}/api/accountApi/login"
        headers = {
            "Content-Type": "application/json;charset=utf-8",
        }
        
        if self._anti_forgery_token:
            headers["antiForgeryToken"] = self._anti_forgery_token
        
        payload = {
            "EmailAddress": email,
            "Password": password,
            "IsServiceStatusReturned": True,
            "ApiActive": True,
            "ApiDown": False,
            "RedirectUrl": "",
            "events": [],
            "formErrors": [],
        }
        
        response = self.session.post(login_url, json=payload, headers=headers)
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid email or password")
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("Errors"):
            error_msg = "; ".join([e.get("Message", str(e)) if isinstance(e, dict) else str(e) for e in data["Errors"]])
            raise AuthenticationError(f"Login failed: {error_msg}")
        
        self._authenticated = True
        return data.get("Content", {})
    
    @property
    def cookies(self) -> Dict[str, str]:
        """Get the current session cookies."""
        return self.session.cookies.get_dict()
    
    def logout(self):
        """Logout from the API.
        
        This invalidates the current session.
        """
        logout_url = f"{self.BASE_URL}/Account/Logout?message=logout"
        self.session.get(logout_url)
    
    def _extract_anti_forgery_token(self, html_content: str) -> None:
        """Extract the anti-forgery token from HTML content."""
        # Look for the token in the page - it's typically in a script or meta tag
        # For now, we'll extract it from the cookie which is simpler
        # The actual token format may vary, so this is a best-effort extraction
        pass
    
    def _ensure_authenticated(self) -> None:
        """Ensure the client is authenticated."""
        if not self._authenticated:
            raise AuthenticationError("Not authenticated. Please call login() first.")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        require_auth: bool = True,
    ) -> Dict[str, Any]:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON request body
            require_auth: Whether authentication is required
            
        Returns:
            Response data
            
        Raises:
            APIError: If the API returns an error
        """
        if require_auth:
            self._ensure_authenticated()
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {}
        
        if method.upper() == "POST" and self._anti_forgery_token:
            headers["antiForgeryToken"] = self._anti_forgery_token
            headers["Content-Type"] = "application/json;charset=utf-8"
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )
        
        if response.status_code == 401:
            raise SessionExpiredError("Session expired. Please login again.")
        
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("Errors"):
            error_msg = "; ".join([e.get("Message", str(e)) for e in data["Errors"]])
            raise APIError(
                f"API error: {error_msg}",
                status_code=response.status_code,
                response=data,
            )
        
        return data.get("Content", {})
    
    def get_locations(self) -> List[Location]:
        """
        Get all locations associated with the account.
        
        Returns:
            List of Location objects
            
        Raises:
            AuthenticationError: If not authenticated
            APIError: If the API returns an error
        """
        data = self._make_request("GET", "/api/locationsapi/getlocations")
        locations_data = data.get("Locations", [])
        return [Location.from_dict(loc) for loc in locations_data]
    
    def get_location(self, location_id: str) -> Location:
        """
        Get detailed information about a specific location.
        
        Args:
            location_id: The location ID
            
        Returns:
            Location object with detailed information
            
        Raises:
            LocationNotFoundError: If the location is not found
            APIError: If the API returns an error
        """
        data = self._make_request(
            "GET",
            "/Api/LocationsApi/GetLocation",
            params={"id": location_id},
        )
        
        if not data:
            raise LocationNotFoundError(f"Location {location_id} not found")
        
        location_data = data.get("Location", {})
        location = Location.from_dict(location_data)
        
        # Add gateways and notification emails
        if "Gateways" in data:
            from .models import Gateway
            location.gateways = [Gateway.from_dict(g) for g in data["Gateways"]]
        
        if "NotificationEmails" in data:
            location.notification_emails = data["NotificationEmails"]
        
        return location
    
    def get_location_system(self, location_id: str) -> Location:
        """
        Get the heating system configuration and zone status for a location.
        
        Args:
            location_id: The location ID
            
        Returns:
            Location object with zones and system status
            
        Raises:
            LocationNotFoundError: If the location is not found
            APIError: If the API returns an error
        """
        data = self._make_request(
            "GET",
            "/Api/LocationsApi/GetLocationSystem",
            params={"id": location_id},
        )
        
        if not data:
            raise LocationNotFoundError(f"Location {location_id} not found")
        
        location_model = data.get("LocationModel", {})
        return Location.from_dict(location_model)
    
    def get_account_info(self) -> UserInfo:
        """
        Get account information for the authenticated user.
        
        Returns:
            UserInfo object
            
        Raises:
            AuthenticationError: If not authenticated
            APIError: If the API returns an error
        """
        data = self._make_request("GET", "/api/accountApi/getAccountInformation")
        user_info_data = data.get("UserInfo", {})
        return UserInfo.from_dict(user_info_data)
    
    def set_zone_temperature(
        self,
        zone_id: str,
        temperature: float,
        permanent: bool = True,
        duration_hours: int = 0,
        duration_minutes: int = 0,
        location_time_offset_minutes: int = 60,
        is_following_schedule: bool = False,
    ) -> None:
        """
        Set the target temperature for a heating zone.
        
        Args:
            zone_id: The zone ID
            temperature: Target temperature in Celsius
            permanent: Whether to hold the temperature permanently (default: True)
            duration_hours: Hours to hold temperature (if not permanent)
            duration_minutes: Minutes to hold temperature (if not permanent)
            location_time_offset_minutes: Time zone offset in minutes (default: 60 for CET)
            
        Raises:
            ZoneNotFoundError: If the zone is not found
            APIError: If the API returns an error
        """
        payload = {
            "zoneId": zone_id,
            "heatTemperature": str(temperature),
            "hotWaterStateIsOn": False,
            "isPermanent": permanent,
            "setUntilHours": f"{duration_hours:02d}",
            "setUntilMinutes": f"{duration_minutes:02d}",
            "locationTimeOffsetMinutes": location_time_offset_minutes,
            "isFollowingSchedule": is_following_schedule,
        }
        
        self._make_request("POST", "/api/ZonesApi/SetZoneTemperature", json_data=payload)
    
    def get_zone(self, location_id: str, zone_id: str) -> Zone:
        """
        Get a specific zone by ID.
        
        Args:
            location_id: The location ID
            zone_id: The zone ID
            
        Returns:
            Zone object
            
        Raises:
            ZoneNotFoundError: If the zone is not found
        """
        location = self.get_location_system(location_id)
        zone = location.get_zone_by_id(zone_id)
        
        if not zone:
            raise ZoneNotFoundError(f"Zone {zone_id} not found in location {location_id}")
        
        return zone
    
    def get_zone_by_name(self, location_id: str, zone_name: str) -> Zone:
        """
        Get a specific zone by name.
        
        Args:
            location_id: The location ID
            zone_name: The zone name
            
        Returns:
            Zone object
            
        Raises:
            ZoneNotFoundError: If the zone is not found
        """
        location = self.get_location_system(location_id)
        zone = location.get_zone_by_name(zone_name)
        
        if not zone:
            raise ZoneNotFoundError(f"Zone '{zone_name}' not found in location {location_id}")
        
        return zone

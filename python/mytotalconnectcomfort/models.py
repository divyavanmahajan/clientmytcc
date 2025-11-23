"""
Data models for the MyTotalConnectComfort API.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Zone:
    """Represents a heating zone (room) in the system."""
    
    id: str
    name: str
    temperature: float
    target_temperature: float
    min_temperature: float
    max_temperature: float
    is_alive: bool
    device_id: Optional[int] = None
    mac_id: Optional[str] = None
    thermostat_model: Optional[str] = None
    has_alerts: bool = False
    has_comm_lost_alert: bool = False
    has_battery_low_alert: bool = False
    has_sensor_failure_alert: bool = False
    override_active: bool = False
    hold_permanently: bool = False
    setpoint_status: int = 0
    thermostat_units: str = "Celsius"
    thermostat_version: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Zone":
        """Create a Zone instance from API response data."""
        return cls(
            id=data.get("Id", ""),
            name=data.get("Name", ""),
            temperature=data.get("Temperature", 0.0),
            target_temperature=data.get("TargetHeatTemperature", 0.0),
            min_temperature=data.get("MinHeatSetpoint", 5.0),
            max_temperature=data.get("MaxHeatSetpoint", 35.0),
            is_alive=data.get("IsAlive", False),
            device_id=data.get("DeviceId"),
            mac_id=data.get("MacId"),
            thermostat_model=data.get("ThermostatModelType"),
            has_alerts=data.get("HasAlerts", False),
            has_comm_lost_alert=data.get("HasCommLostAlert", False),
            has_battery_low_alert=data.get("HasBatteryLowAlert", False),
            has_sensor_failure_alert=data.get("HasSensorFailureAlert", False),
            override_active=data.get("OverrideActive", False),
            hold_permanently=data.get("HoldTemperaturePermanently", False),
            setpoint_status=data.get("SetPointStatus", 0),
            thermostat_units=data.get("ThermostatUnits", "Celsius"),
            thermostat_version=data.get("ThermostatVersion"),
        )


@dataclass
class Gateway:
    """Represents a gateway device."""
    
    id: str
    mac_id: str
    crc: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "Gateway":
        """Create a Gateway instance from API response data."""
        return cls(
            id=data.get("Id", ""),
            mac_id=data.get("MacId", ""),
            crc=data.get("Crc", ""),
        )


@dataclass
class Location:
    """Represents a location (home) with heating zones."""
    
    id: str
    name: str
    city: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    street_address: Optional[str] = None
    owner_name: Optional[str] = None
    time_zone_id: Optional[str] = None
    time_zone_display_name: Optional[str] = None
    heating_system_type: int = 1
    zones: List[Zone] = None
    gateways: List[Gateway] = None
    notification_emails: List[str] = None
    
    def __post_init__(self):
        if self.zones is None:
            self.zones = []
        if self.gateways is None:
            self.gateways = []
        if self.notification_emails is None:
            self.notification_emails = []
    
    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        """Create a Location instance from API response data."""
        zones_data = data.get("Zones", [])
        zones = [Zone.from_dict(z) for z in zones_data] if zones_data else []
        
        gateways_data = data.get("Gateways", [])
        gateways = [Gateway.from_dict(g) for g in gateways_data] if gateways_data else []
        
        return cls(
            id=data.get("Id", ""),
            name=data.get("Name", ""),
            city=data.get("City"),
            country=data.get("Country"),
            postcode=data.get("Postcode"),
            street_address=data.get("StreetAddress"),
            owner_name=data.get("OwnerName"),
            time_zone_id=data.get("TimeZoneId"),
            time_zone_display_name=data.get("TimeZoneDisplayName"),
            heating_system_type=data.get("HeatingSystemType", 1),
            zones=zones,
            gateways=gateways,
            notification_emails=data.get("NotificationEmails", []),
        )
    
    def get_zone_by_id(self, zone_id: str) -> Optional[Zone]:
        """Get a zone by its ID."""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None
    
    def get_zone_by_name(self, name: str) -> Optional[Zone]:
        """Get a zone by its name."""
        for zone in self.zones:
            if zone.name.lower() == name.lower():
                return zone
        return None


@dataclass
class UserInfo:
    """Represents user account information."""
    
    username: str
    first_name: str
    last_name: str
    street_address: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    user_language: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserInfo":
        """Create a UserInfo instance from API response data."""
        return cls(
            username=data.get("Username", ""),
            first_name=data.get("FirstName", ""),
            last_name=data.get("LastName", ""),
            street_address=data.get("StreetAddress"),
            city=data.get("City"),
            postcode=data.get("Postcode"),
            country_id=data.get("CountryId"),
            country_name=data.get("CountryName"),
            user_language=data.get("UserLanguage"),
        )

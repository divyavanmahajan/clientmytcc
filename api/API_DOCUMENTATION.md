# MyTotalConnectComfort API Documentation

## Overview

This document describes the API endpoints used by the MyTotalConnectComfort web application for managing heating zones and thermostats. This API is for the **International Honeywell Evohome** system, which is provided by **Resideo** (who licensed the Honeywell brand). This is specifically for the international version accessible via `international.mytotalconnectcomfort.com`.

**Base URL**: `https://international.mytotalconnectcomfort.com`

> **Note**: This documentation covers the international Evohome system. North American systems may use different endpoints.

## Authentication

The API uses cookie-based authentication with the following cookies:
- `SessionCookie` - Session authentication token (expires in 1 hour)
- `RefreshCookie` - Refresh token for session renewal (expires in 6 months)
- `__RequestVerificationToken` - CSRF protection token

Additionally, POST requests require an `antiForgeryToken` header for CSRF protection.

---

## API Endpoints

### 1. Login

**Endpoint**: `POST /api/accountApi/login`

**Description**: Authenticates a user and establishes a session.

**Request Headers**:
- `Content-Type: application/json;charset=utf-8`
- `antiForgeryToken: <token>`
- `X-Requested-With: XMLHttpRequest`

**Request Body**:
```json
{
  "EmailAddress": "user@example.com",
  "Password": "password",
  "IsServiceStatusReturned": true,
  "ApiActive": true,
  "ApiDown": false,
  "RedirectUrl": "",
  "events": [],
  "formErrors": []
}
```

**Response** (200 OK):
```json
{
  "Content": {
    "UserId": "3194795",
    "DisplayName": "TCC User",
    "UserName": "user@example.com",
    "LatestEulaAccepted": null,
    "AccessToken": "",
    "RefreshToken": "",
    "Reauthenticated": false,
    "RedirectUri": null,
    "AuthorizationCode": null,
    "GrantType": null,
    "ExpiresIn": null,
    "ResourceUri": null
  },
  "Errors": null,
  "RedirectUrl": "https://international.mytotalconnectcomfort.com/Locations",
  "CurrentCulture": null
}
```

**Response Cookies**:
- `SessionCookie` (expires in 1 hour)
- `RefreshCookie` (expires in 6 months)

---

### 2. Delete Remember Me Cookie

**Endpoint**: `GET /api/accountApi/deleteRememberMeCookie`

**Description**: Removes the "Remember Me" cookie.

**Response** (200 OK): Empty response with status 200

**Response Cookies**:
- `RememberMeCookie` (expired)

---

### 3. Get Locations

**Endpoint**: `GET /api/locationsapi/getlocations`

**Description**: Retrieves all locations (homes) associated with the authenticated user.

**Response** (200 OK):
```json
{
  "Content": {
    "Locations": [
      {
        "Name": "Home",
        "Id": "1232176",
        "SystemDeviceId": null,
        "TimeOffset": 0,
        "HasGateways": true,
        "HasTempControlSystem": false,
        "HasZones": false,
        "IsDefault": false,
        "City": "TCC City",
        "Country": "Netherlands",
        "CountryId": null,
        "Postcode": null,
        "StreetAddress": null,
        "OwnerName": null,
        "TimeZoneId": null,
        "TimeZoneDisplayName": null,
        "HeatingSystemType": 1,
        "Zones": [
          {
            "Id": "5211675",
            "DeviceId": 5211675,
            "Name": "Livingroom",
            "MacId": "B82CA06CB358",
            "ThermostatModelType": "Evo",
            "IsAlive": true,
            "HasAlerts": false,
            "HasCommLostAlert": false,
            "HasBatteryLowAlert": false,
            "HasSensorFailureAlert": false,
            "Temperature": 19.5,
            "MinHeatSetpoint": 5.0,
            "MaxHeatSetpoint": 35.0,
            "MaxCoolSetpoint": 0.0,
            "MinCoolSetpoint": 0.0,
            "TargetHeatTemperature": 21.0,
            "TargetCoolTemperature": null,
            "SetpointDeadband": null,
            "ThermostatType": 0,
            "OverrideActive": true,
            "HoldTemperaturePermanently": true,
            "SetPointStatus": 2,
            "NextHeatSetPointTime": null,
            "NextHeatSetPointTimeFormatted": null,
            "DomesticHotWaterOn": 0.0,
            "DomesticHotWaterState": 0,
            "CurrentFanSetting": null,
            "FanSettingCanBeChanged": null,
            "AllowedFanSettings": null,
            "AllowedThermostatModes": [3, 4],
            "ThermostatUnits": "Celsius",
            "ThermostatVersion": "EvoTouch"
          }
        ],
        "Type": 1,
        "Current": false,
        "IsOwner": true,
        "QuickActionStatus": null,
        "IsChecked": false,
        "SystemModesConfiguration": null,
        "FanModeStatus": null,
        "LocationViewType": 0,
        "SupportsDaylightSaving": false,
        "UseDaylightSavingSwitch": false,
        "AllActiveFaults": null,
        "AlertCount": 0,
        "HasCommLostSystemOrGatewayAlert": false,
        "HasSecuritySystem": false,
        "SecuritySystemId": null,
        "LocationDate": null,
        "ShouldShowAdvertisement": false,
        "SubscriptionEndDate": null
      }
    ]
  },
  "Errors": null,
  "RedirectUrl": null,
  "CurrentCulture": null
}
```

---

### 4. Get Location Details

**Endpoint**: `GET /Api/LocationsApi/GetLocation?id={locationId}`

**Description**: Retrieves detailed information about a specific location.

**Query Parameters**:
- `id` (required): Location ID

**Response** (200 OK):
```json
{
  "Content": {
    "NotificationEmails": [
      "user1@example.com",
      "user2@example.com"
    ],
    "Location": {
      "Name": "Home",
      "Id": "1232176",
      "SystemDeviceId": null,
      "TimeOffset": 0,
      "HasGateways": false,
      "HasTempControlSystem": false,
      "HasZones": false,
      "IsDefault": false,
      "City": "TCC City",
      "Country": "Netherlands",
      "CountryId": null,
      "Postcode": "6267BM",
      "StreetAddress": "Streetname 123",
      "OwnerName": "TCC User Lastname",
      "TimeZoneId": "WEuropeStandardTime",
      "TimeZoneDisplayName": "(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna",
      "HeatingSystemType": 1
    },
    "Gateways": [
      {
        "Id": "3795953",
        "MacId": "B82CA06CB358",
        "Crc": "9C26"
      }
    ],
    "SecuritySystem": {
      "IsLinked": false
    }
  },
  "Errors": null,
  "RedirectUrl": null,
  "CurrentCulture": null
}
```

---

### 5. Get Account Information

**Endpoint**: `GET /api/accountApi/getAccountInformation`

**Description**: Retrieves account information for the authenticated user.

**Response** (200 OK):
```json
{
  "Content": {
    "UserInfo": {
      "UserId": null,
      "Username": "user@example.com",
      "FirstName": "TCC User",
      "LastName": "Lastname",
      "StreetAddress": "Streetname 123",
      "City": "TCC City",
      "Postcode": "6267BM",
      "CountryId": 1,
      "CountryName": "Netherlands",
      "UserLanguage": 2
    },
    "Friends": [],
    "Contractors": []
  },
  "Errors": null,
  "RedirectUrl": null,
  "CurrentCulture": null
}
```

---

### 6. Get Location System

**Endpoint**: `GET /Api/LocationsApi/GetLocationSystem?id={locationId}`

**Description**: Retrieves the heating system configuration and zone status for a location.

**Query Parameters**:
- `id` (required): Location ID

**Response** (200 OK):
```json
{
  "Content": {
    "LocationModel": {
      "Id": "1232176",
      "SystemDeviceId": "5211687",
      "TimeOffset": 60,
      "HeatingSystemType": 1,
      "Zones": [
        {
          "Id": "5211675",
          "DeviceId": 0,
          "Name": "Livingroom",
          "IsAlive": true,
          "HasAlerts": false,
          "Temperature": 19.5,
          "MinHeatSetpoint": 5.0,
          "MaxHeatSetpoint": 35.0,
          "TargetHeatTemperature": 21.0,
          "ThermostatType": 0,
          "OverrideActive": true,
          "HoldTemperaturePermanently": true,
          "SetPointStatus": 2
        }
      ],
      "QuickActionStatus": {
        "QuickAction": 5,
        "QuickActionNextTime": null,
        "HasQuickActionChanged": false,
        "IsQuickActionActive": false,
        "QuickActionNextTimeFormatted": null
      },
      "SystemModesConfiguration": [
        {
          "SystemMode": 0,
          "CanBePermanent": true,
          "CanBeTemporary": true,
          "MaxDuration": "1.00:00:00",
          "TimingResolution": "01:00:00",
          "TimingMode": 1
        }
      ],
      "AllActiveFaults": [
        {
          "FaultType": 16,
          "Time": "2025-11-14T02:04:14",
          "DeviceType": 0,
          "DeviceId": "5211675",
          "Name": "Livingroom"
        }
      ]
    }
  },
  "Errors": null,
  "RedirectUrl": null,
  "CurrentCulture": null
}
```

---

### 7. Set Zone Temperature

**Endpoint**: `POST /api/ZonesApi/SetZoneTemperature`

**Description**: Sets the target temperature for a specific zone.

**Request Headers**:
- `Content-Type: application/json;charset=utf-8`
- `antiForgeryToken: <token>`
- `X-Requested-With: XMLHttpRequest`

**Request Body**:
```json
{
  "zoneId": "5211682",
  "heatTemperature": "17.5",
  "hotWaterStateIsOn": false,
  "isPermanent": true,
  "setUntilHours": "00",
  "setUntilMinutes": "00",
  "locationTimeOffsetMinutes": 60,
  "isFollowingSchedule": false
}
```

**Response** (200 OK):
```json
{
  "Errors": null,
  "RedirectUrl": null,
  "ReauthenticatedAccessToken": null,
  "ReauthenticatedRefreshToken": null
}
```

---

## Data Models

### Zone Object

| Field | Type | Description |
|-------|------|-------------|
| Id | string | Unique zone identifier |
| DeviceId | integer | Device ID for the zone |
| Name | string | Zone name (e.g., "Livingroom") |
| MacId | string | MAC address of the thermostat |
| ThermostatModelType | string | Model type (e.g., "Evo") |
| IsAlive | boolean | Whether the zone is online |
| HasAlerts | boolean | Whether there are active alerts |
| Temperature | number | Current temperature in Celsius |
| MinHeatSetpoint | number | Minimum allowed temperature |
| MaxHeatSetpoint | number | Maximum allowed temperature |
| TargetHeatTemperature | number | Target temperature setpoint |
| OverrideActive | boolean | Whether manual override is active |
| HoldTemperaturePermanently | boolean | Whether temperature is held permanently |
| SetPointStatus | integer | Status code (0=following schedule, 2=override) |
| ThermostatUnits | string | Temperature units ("Celsius" or "Fahrenheit") |
| ThermostatVersion | string | Thermostat version (e.g., "EvoTouch") |

### Location Object

| Field | Type | Description |
|-------|------|-------------|
| Id | string | Unique location identifier |
| Name | string | Location name |
| City | string | City name |
| Country | string | Country name |
| Postcode | string | Postal code |
| StreetAddress | string | Street address |
| TimeZoneId | string | Time zone identifier |
| HeatingSystemType | integer | Type of heating system (1=Evohome) |
| Zones | array | Array of Zone objects |

---

## Error Handling

All endpoints return errors in the following format:

```json
{
  "Content": null,
  "Errors": [
    {
      "Code": "ERROR_CODE",
      "Message": "Error description"
    }
  ],
  "RedirectUrl": null,
  "CurrentCulture": null
}
```

---

## Notes

1. **CSRF Protection**: All POST requests require both the `__RequestVerificationToken` cookie and the `antiForgeryToken` header.

2. **Session Management**: Sessions expire after 1 hour. Use the `RefreshCookie` to maintain long-term access.

3. **Temperature Units**: All temperatures are in Celsius by default. The `ThermostatUnits` field indicates the unit system.

4. **Zone Status Codes**:
   - `SetPointStatus: 0` - Following schedule
   - `SetPointStatus: 2` - Manual override active

5. **Fault Types**: The system tracks various fault types (15, 16, 17, 18) for different issues like communication loss, battery low, etc.

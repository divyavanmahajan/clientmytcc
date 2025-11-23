"""
Basic usage example for the MyTotalConnectComfort API client.
"""

from mytotalconnectcomfort import Client
from mytotalconnectcomfort.exceptions import (
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
)


def main():
    """Demonstrate basic usage of the API client."""
    
    # Create a client instance
    client = Client()
    
    # Login with your credentials
    # IMPORTANT: Replace with your actual credentials
    email = "your-email@example.com"
    password = "your-password"
    
    try:
        print("Logging in...")
        user_data = client.login(email, password)
        print(f"[OK] Logged in as: {user_data.get('DisplayName', 'User')}")
        print()
        
        # Get all locations
        print("Fetching locations...")
        locations = client.get_locations()
        print(f"[OK] Found {len(locations)} location(s)")
        print()
        
        for location in locations:
            print(f"Location: {location.name}")
            print(f"  ID: {location.id}")
            print(f"  City: {location.city}, {location.country}")
            print(f"  Zones: {len(location.zones)}")
            print()
            
            # Get detailed system information for this location
            print(f"Fetching system details for {location.name}...")
            system = client.get_location_system(location.id)
            
            # Display zone information
            for zone in system.zones:
                status = "[Online]" if zone.is_alive else "[Offline]"
                override = " (Override Active)" if zone.override_active else ""
                
                print(f"  Zone: {zone.name} {status}{override}")
                print(f"    Current: {zone.temperature}°C")
                print(f"    Target:  {zone.target_temperature}°C")
                print(f"    Range:   {zone.min_temperature}°C - {zone.max_temperature}°C")
                
                if zone.has_alerts:
                    print(f"    [WARNING] Has alerts!")
                
                print()
            
            # Example: Set temperature for a specific zone
            if system.zones:
                example_zone = system.zones[0]
                new_temp = 21.0
                
                print(f"Example: Setting {example_zone.name} to {new_temp}°C...")
                try:
                    client.set_zone_temperature(
                        zone_id=example_zone.id,
                        temperature=new_temp,
                        permanent=True,
                    )
                    print(f"[OK] Temperature set successfully!")
                except APIError as e:
                    print(f"[ERROR] Failed to set temperature: {e}")
                print()
        
        # Get account information
        print("Fetching account information...")
        account = client.get_account_info()
        print(f"[OK] Account: {account.first_name} {account.last_name}")
        print(f"  Email: {account.username}")
        print(f"  Location: {account.city}, {account.country_name}")
        print()
        
    except AuthenticationError as e:
        print(f"[ERROR] Authentication failed: {e}")
        print("Please check your email and password.")
    except ZoneNotFoundError as e:
        print(f"[ERROR] Zone not found: {e}")
    except APIError as e:
        print(f"[ERROR] API error: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

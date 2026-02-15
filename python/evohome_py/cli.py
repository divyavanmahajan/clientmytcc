"""Command-line interface for MyTotalConnectComfort."""

import sys
import os
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .client import Client
from .exceptions import (
    MyTotalConnectComfortError,
    AuthenticationError,
    ZoneNotFoundError,
)
from .config import Config
from .utils import TemperatureType, DurationType, fahrenheit_to_celsius
from .session import save_session, load_session, clear_session

console = Console()
config = Config()


import time

class AliasedGroup(click.Group):
    def command(self, *args, **kwargs):
        aliases = kwargs.pop('aliases', [])
        decorator = super().command(*args, **kwargs)
        def _decorator(f):
            cmd = decorator(f)
            cmd.aliases = aliases
            return cmd
        return _decorator

    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)
        if rv is not None:
            return rv
        for name, cmd in self.commands.items():
            if hasattr(cmd, 'aliases') and cmd_name in cmd.aliases:
                return cmd
        return None

    def resolve_command(self, ctx, args):
        # Always return the full command name, not the alias
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args

@click.group(cls=AliasedGroup)
@click.version_option()
@click.pass_context
def cli(ctx):
    """MyTotalConnectComfort CLI for Evohome heating control."""
    ctx.ensure_object(dict)
    ctx.obj['start_time'] = time.time()

@cli.result_callback()
def process_result(result, **kwargs):
    ctx = click.get_current_context()
    if 'start_time' in ctx.obj:
        duration = time.time() - ctx.obj['start_time']
        rprint(f"\n[dim]Done in {duration:.2f}s[/dim]")


@cli.command()
@click.argument("email", required=False)
@click.option("--password", prompt=False, hide_input=True, help="Password")
def login(email: Optional[str], password: Optional[str]):
    """Authenticate with MyTotalConnectComfort."""
    try:
        # Check env vars if args missing
        if not email:
            email = os.environ.get("EVOHOME_USER") or os.environ.get("EVOHOME_EMAIL")
            if not email:
                email = click.prompt("Email")
        
        if not password:
            password = os.environ.get("EVOHOME_PASSWORD")
            if not password:
                password = click.prompt("Password", hide_input=True)

        client = Client()
        result = client.login(email, password)
        
        # Save email to config
        config.set("email", email)
        config.save()
        
        # Save session
        save_session(email, client.cookies)
        
        rprint(f"[green][OK][/green] Logged in as: {result['DisplayName']}")
        rprint(f"[dim]User ID: {result['UserId']}[/dim]")
    except AuthenticationError as e:
        rprint(f"[red][ERROR][/red] Authentication failed: {e}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
def logout():
    """Clear stored credentials."""
    config.clear()
    config.save()
    clear_session()
    rprint("[green][OK][/green] Logged out")


@cli.command()
def locations():
    """List all locations."""
    try:
        client = _get_authenticated_client()
        locs = client.get_locations()
        
        table = Table(title="Locations")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("City", style="yellow")
        table.add_column("Zones", justify="right")
        
        for loc in locs:
            table.add_row(
                loc.id,
                loc.name,
                loc.city or "-",
                str(len(loc.zones))
            )
        
        console.print(table)
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)








@cli.command()
def account():
    """Show account information."""
    try:
        client = _get_authenticated_client()
        info = client.get_account_info()
        
        rprint(f"[bold]Account Information[/bold]")
        rprint(f"Name: {info.first_name} {info.last_name}")
        rprint(f"Email: {info.username}")
        if info.city and info.country_name:
            rprint(f"Location: {info.city}, {info.country_name}")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("zone_id", required=False)
@click.argument("temperature", type=TemperatureType(), required=False)
@click.option("--duration", type=DurationType(), help="Duration (e.g., '2h', '30m')")
@click.option("--location", "location_id", help="Location ID (for zone selection)")
def set(zone_id: Optional[str], temperature: Optional[float], duration: Optional[tuple], location_id: Optional[str]):
    """Set zone temperature."""
    try:
        client = _get_authenticated_client()
        
        # If zone_id not provided, help user select
        if not zone_id:
            (location_id,location_name) = _select_location(client, location_id)
            zone_id = _select_zone(client, location_id)
        
        # If temperature not provided, prompt
        if temperature is None:
            temp_input = click.prompt("Enter temperature (e.g., 21C, 70F)")
            from .utils import parse_temperature, fahrenheit_to_celsius
            temp, unit = parse_temperature(temp_input)
            if unit == 'F':
                temp = fahrenheit_to_celsius(temp)
            temperature = temp
        
        # Parse duration
        if duration:
            hours, minutes = duration
            permanent = False
        else:
            hours, minutes = 0, 0
            permanent = True
        
        client.set_zone_temperature(
            zone_id=zone_id,
            temperature=temperature,
            permanent=permanent,
            duration_hours=hours,
            duration_minutes=minutes
        )
        
        if permanent:
            rprint(f"[green][OK][/green] Set zone {zone_id} to {temperature}°C (permanent)")
            rprint(f"[dim]Command to skip selection: evohome_py set {zone_id} {temperature}C[/dim]")
        else:
            total_mins = hours * 60 + minutes
            rprint(f"[green][OK][/green] Set zone {zone_id} to {temperature}°C for {total_mins} minutes")
            rprint(f"[dim]Command to skip selection: evohome_py set {zone_id} {temperature}C --duration {hours}h{minutes}m[/dim]")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("temp", type=TemperatureType(), required=False, default="22C")
@click.option("--location-id", "-l", help="Location ID")
@click.option("--duration", type=float, default=2, help="Duration in hours (default: 2)")
@click.option("--override", is_flag=True, help="Force change even if zone is off (5°C)")
@click.pass_context
def boost(ctx, temp: float, location_id: Optional[str], duration: float, override: bool):
    """Boost all zones in a location."""
    try:
        client = _get_authenticated_client()
        (location_id,location_name) = _select_location(client, location_id)
        system = client.get_location_system(location_id)
        
        count = 0
        skipped = 0
        for zone in system.zones:
            if zone.is_alive:
                # Skip if target is 5.0 (off/frost protect) unless override is set
                if abs(zone.target_temperature - 5.0) < 0.1 and not override:
                    rprint(f"[blue][INFO][/blue] Skipped {zone.name} (Target is 5.0°C). Use --override to force.")
                    skipped += 1
                    continue

                client.set_zone_temperature(
                    zone_id=zone.id,
                    temperature=temp,
                    permanent=False,
                    duration_hours=int(duration),
                    duration_minutes=int((duration - int(duration)) * 60)
                )
                count += 1
                rprint(f"[green][OK][/green] Boosted {zone.name} to {temp}°C for {duration}h")
        
        rprint(f"\n[bold green]Boosted {count} zones ({skipped} skipped)[/bold green]")
        
        # Show status
        print()
        ctx.invoke(monitor, location_id=location_id, format="table")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("temp", type=TemperatureType(), required=False, default="18C")
@click.option("--location-id", "-l", help="Location ID")
@click.option("--override", is_flag=True, help="Force change even if zone is off (5°C)")
@click.pass_context
def eco(ctx, temp: float, location_id: Optional[str], override: bool):
    """Set all zones to energy-saving temperature."""
    try:
        client = _get_authenticated_client()
        (location_id,location_name) = _select_location(client, location_id)
        system = client.get_location_system(location_id)
        
        count = 0
        skipped = 0
        for zone in system.zones:
            if zone.is_alive and zone.target_temperature > temp:
                # Skip if target is 5.0 (off/frost protect) unless override is set
                if abs(zone.target_temperature - 5.0) < 0.1 and not override:
                    rprint(f"[blue][INFO][/blue] Skipped {zone.name} (Target is 5.0°C). Use --override to force.")
                    skipped += 1
                    continue

                client.set_zone_temperature(
                    zone_id=zone.id,
                    temperature=temp,
                    permanent=True
                )
                count += 1
                rprint(f"[green][OK][/green] Set {zone.name} to eco mode ({temp}°C)")
        
        rprint(f"\n[bold green]Set {count} zones to eco mode ({skipped} skipped)[/bold green]")
        
        # Show status
        print()
        ctx.invoke(monitor, location_id=location_id, format="table")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command(name="monitor", aliases=["zones"])
@click.option("--location-id", "-l", help="Location ID")
@click.option("--format", "-f", type=click.Choice(["table", "json"]), default="table")
def monitor(location_id: Optional[str], format: str):
    """Monitor zone temperatures (alias: zones)."""
    try:
        client = _get_authenticated_client()
        (location_id,location_name) = _select_location(client, location_id)
        system = client.get_location_system(location_id)
        
        if format == "json":
            report = []
            for zone in system.zones:
                diff = zone.target_temperature - zone.temperature
                status = "off" if zone.target_temperature == 5.0 else "heating" if diff > 0.5 else "stable"
                report.append({ 
                    "name": zone.name,
                    "current": zone.temperature,
                    "target": zone.target_temperature,
                    "status": status,
                    "online": zone.is_alive
                })
            print(json.dumps(report, indent=2))
        else:
            table = Table(title=f"Temperature Monitor: {location_name}")
            table.add_column("Zone", style="green")
            table.add_column("Current", justify="right")
            table.add_column("Target", justify="right")
            table.add_column("Diff", justify="right")
            table.add_column("Status", style="yellow")
            table.add_column("Online")
            table.add_column("ID", justify="right")
            
            for zone in system.zones:
                diff = zone.target_temperature - zone.temperature
                status = "Off" if zone.target_temperature == 5.0 else "Heating" if diff > 0.5 else "Stable"
                online = "[green]Online[/green]" if zone.is_alive else "[red]Offline[/red]"
                
                # Format temperature, 128.0 means invalid/offline
                if zone.temperature >= 128.0:
                    current_temp = "--"
                    diff_str = "--"
                else:
                    current_temp = f"{zone.temperature:.1f}°C"
                    diff_str = f"{diff:+.1f}°C"
                
                table.add_row(
                    zone.name,
                    current_temp,
                    f"{zone.target_temperature:.1f}°C",
                    diff_str,
                    status,
                    online,
                    str(zone.id)
                )
            
            console.print(table)
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("temp", type=TemperatureType(), required=False, default="12C")
@click.option("--location-id", "-l", help="Location ID")
@click.option("--override", is_flag=True, help="Force change even if zone is off (5°C)")
@click.pass_context
def vacation(ctx, temp: float, location_id: Optional[str], override: bool):
    """Set all zones to frost protection (vacation mode)."""
    try:
        client = _get_authenticated_client()
        (location_id,location_name) = _select_location(client, location_id)
        system = client.get_location_system(location_id)
        
        count = 0
        skipped = 0
        for zone in system.zones:
            if zone.is_alive:
                # Skip if target is 5.0 (off/frost protect) unless override is set
                if abs(zone.target_temperature - 5.0) < 0.1 and not override:
                    rprint(f"[blue][INFO][/blue] Skipped {zone.name} (Target is 5.0°C). Use --override to force.")
                    skipped += 1
                    continue

                client.set_zone_temperature(
                    zone_id=zone.id,
                    temperature=temp,
                    permanent=True
                )
                count += 1
        
        rprint(f"[green][OK][/green] Vacation mode activated ({temp}°C)")
        rprint(f"Set {count} zones to frost protection ({skipped} skipped)")
        
        # Show status
        print()
        ctx.invoke(monitor, location_id=location_id, format="table")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("location_id", required=False)
def schedule(location_id: Optional[str]):
    """Reset all zones to follow their programmed schedule."""
    try:
        client = _get_authenticated_client()
        (location_id,location_name) = _select_location(client, location_id)
        system = client.get_location_system(location_id)
        
        count = 0
        for zone in system.zones:
            if zone.is_alive:
                # Set to follow schedule by setting permanent=False with 0 duration
                # This tells the API to resume following the schedule
                client.set_zone_temperature(
                    zone_id=zone.id,
                    temperature=0,  # Temperature ignored when following schedule
                    permanent=False,
                    is_following_schedule=True,
                    duration_hours=0,
                    duration_minutes=0
                )
                count += 1
                rprint(f"[green][OK][/green] {zone.name} now following schedule")
        
        rprint(f"\n[bold green]Reset {count} zones to follow schedule[/bold green]")
    except MyTotalConnectComfortError as e:
        rprint(f"[red][ERROR][/red] {e}")
        sys.exit(1)


@cli.group()
def config_cmd():
    """Manage configuration."""
    pass


@config_cmd.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value."""
    config.set(key, value)
    config.save()
    rprint(f"[green][OK][/green] Set {key} = {value}")


@config_cmd.command("get")
@click.argument("key")
def config_get(key: str):
    """Get a configuration value."""
    value = config.get(key)
    if value:
        print(value)
    else:
        rprint(f"[yellow][WARNING][/yellow] Key '{key}' not found")
        sys.exit(1)


# Global cache for authenticated client
_cached_client: Optional[Client] = None

@config_cmd.command("list")
def config_list():
    """List all configuration."""
    data = config.load()
    if data:
        for key, value in data.items():
            rprint(f"{key} = {value}")
    else:
        rprint("[dim]No configuration set[/dim]")


def _get_authenticated_client() -> Client:
    """Get an authenticated client instance, using a cached client if available."""
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    # 1. Try loading session
    session = load_session()
    if session:
        from .session import cookies_to_dict
        client = Client(cookies=cookies_to_dict(session.cookies))
        try:
            # Validate session with a lightweight call
            client.get_account_info()
            _cached_client = client
            return client
        except (MyTotalConnectComfortError, Exception):
            rprint("[yellow][WARNING][/yellow] Session expired, attempting auto-login...")
            # Fall through to env var login

    # Try to get email from config or env
    email = config.get("email")
    if not email:
        email = os.environ.get("EVOHOME_USER") or os.environ.get("EVOHOME_EMAIL")
    
    if not email:
        rprint("[red][ERROR][/red] Not logged in. Run 'evohome_py login' or set EVOHOME_USER/EVOHOME_PASSWORD.")
        sys.exit(1)
    
    # Try to get password from env
    password = os.environ.get("EVOHOME_PASSWORD")
    
    if not password:
        # If no password in env, we can't auto-login without session persistence
        rprint("[red][ERROR][/red] Session expired and EVOHOME_PASSWORD not set.")
        rprint("[yellow]Please run 'evohome_py login' or set EVOHOME_PASSWORD.[/yellow]")
        sys.exit(1)
        
    try:
        client = Client()
        client.login(email, password)
        # Save session for next time
        save_session(email, client.cookies)
        _cached_client = client
        return client
    except AuthenticationError as e:
        rprint(f"[red][ERROR][/red] Auto-login failed: {e}")
        sys.exit(1)

_cached_location: Optional[Location] = None
def _select_location(client: Client, location_id: Optional[str] = None) -> tuple[str, str]:
    """Select a location, using smart defaults.
    
    Args:
        client: Authenticated client
        location_id: Optional location ID. If None, will auto-select or prompt.
    
    Returns:
        Selected location ID
    """
    global _cached_location
    if _cached_location:
        return (_cached_location.id, _cached_location.name)
    

    # Check config for default
    if location_id is None or not isinstance(location_id, str):
        default_location = config.get("default_location")
        if default_location:
            location_id= default_location
    
    # Get all locations
    locations = client.get_locations()
    
    if len(locations) == 0:
        rprint("[red][ERROR][/red] No locations found")
        sys.exit(1)
    
    # Check location is valid
    for i, loc in enumerate(locations, 1):
        if loc.id == location_id:
            _cached_location= loc
            return (_cached_location.id, _cached_location.name)
        rprint(f"  {i}. {loc.name} ({loc.city or 'Unknown'})")
    # Auto-select if only one location
    if len(locations) == 1:
        rprint(f"[dim]Using location: {locations[0].name}[/dim]")
        _cached_location= locations[0]
        return (_cached_location.id, _cached_location.name)
    
    # Multiple locations - let user select
    rprint("[bold]Select a location:[/bold]")
    for i, loc in enumerate(locations, 1):
        rprint(f"  {i}. {loc.name} ({loc.city or 'Unknown'})")
    
    while True:
        try:
            choice = click.prompt("Enter number", type=int)
            if 1 <= choice <= len(locations):
                selected = locations[choice - 1]
                rprint(f"[green]Selected:[/green] {selected.name}")
                _cached_location= selected
                return (_cached_location.id, _cached_location.name)
            else:
                rprint(f"[red]Please enter a number between 1 and {len(locations)}[/red]")
        except (ValueError, click.Abort):
            rprint("[red]Invalid input[/red]")
            sys.exit(1)


def _select_zone(client: Client, location_id: str, zone_id: Optional[str] = None) -> str:
    """Select a zone, using smart defaults.
    
    Args:
        client: Authenticated client
        location_id: Location ID
        zone_id: Optional zone ID or name. If None, will prompt user.
    
    Returns:
        Selected zone ID
    """
    if zone_id:
        # Check if it's a numeric ID or a name/prefix
        if zone_id.isdigit():
            return zone_id
        else:
            # Try to match by name (case-insensitive prefix)
            system = client.get_location_system(location_id)
            zone_id_lower = zone_id.lower()
            matches = [z for z in system.zones if z.name.lower().startswith(zone_id_lower)]
            
            if len(matches) == 0:
                rprint(f"[red][ERROR][/red] No zone found matching '{zone_id}'")
                sys.exit(1)
            elif len(matches) == 1:
                rprint(f"[dim]Using zone: {matches[0].name}[/dim]")
                return matches[0].id
            else:
                # Multiple matches - let user select
                rprint(f"[yellow]Multiple zones match '{zone_id}':[/yellow]")
                for i, zone in enumerate(matches, 1):
                    status = "[green]Online[/green]" if zone.is_alive else "[red]Offline[/red]"
                    current_temp = "--" if zone.temperature >= 128.0 else f"{zone.temperature:>5.1f}°C"
                    rprint(f"{i:>2}.  {zone.id:>8}: ({current_temp} --> {zone.target_temperature:>5.1f}°C) {zone.name:<20}")
                
                while True:
                    try:
                        choice = click.prompt("Enter number", type=int)
                        if 1 <= choice <= len(matches):
                            selected = matches[choice - 1]
                            rprint(f"[green]Selected:[/green] {selected.name}")
                            return selected.id
                        else:
                            rprint(f"[red]Please enter a number between 1 and {len(matches)}[/red]")
                    except (ValueError, click.Abort):
                        rprint("[red]Invalid input[/red]")
                        sys.exit(1)
    
    # Get all zones for location
    system = client.get_location_system(location_id)
    
    if len(system.zones) == 0:
        rprint("[red][ERROR][/red] No zones found")
        sys.exit(1)
    
    if len(system.zones) == 1:
        rprint(f"[dim]Using zone: {system.zones[0].name}[/dim]")
        return system.zones[0].id
    
    # Let user select zone
    rprint(f"[bold]Select a zone in {system.name}:[/bold]")
    for i, zone in enumerate(system.zones, 1):
        status = "[green]Online[/green]" if zone.is_alive else "[red]Offline[/red]"
        current_temp = "--" if zone.temperature >= 128.0 else f"{zone.temperature:>5.1f}°C"
        rprint(f"{i:>2}.  {zone.id:>8}: ({current_temp} --> {zone.target_temperature:>5.1f}°C) {zone.name:<20}")
    
    while True:
        try:
            choice = click.prompt("Enter number", type=int)
            if 1 <= choice <= len(system.zones):
                selected = system.zones[choice - 1]
                rprint(f"[green]Selected:[/green] {selected.name}")
                return selected.id
            else:
                rprint(f"[red]Please enter a number between 1 and {len(system.zones)}[/red]")
        except (ValueError, click.Abort):
            rprint("[red]Invalid input[/red]")
            sys.exit(1)


if __name__ == "__main__":
    cli()

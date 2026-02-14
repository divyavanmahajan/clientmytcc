"""Utility functions and custom types for the CLI."""

import click
import re
from typing import Tuple


def parse_temperature(temp_str: str) -> Tuple[float, str]:
    """Parse temperature string with optional unit.
    
    Args:
        temp_str: Temperature string (e.g., "21", "21C", "70F")
    
    Returns:
        Tuple of (temperature value, unit)
        Unit is 'C' or 'F', defaults to 'C' if not specified
    
    Examples:
        >>> parse_temperature("21")
        (21.0, 'C')
        >>> parse_temperature("21C")
        (21.0, 'C')
        >>> parse_temperature("70F")
        (70.0, 'F')
    """
    temp_str = temp_str.strip().upper()
    
    # Match number with optional unit
    match = re.match(r'^([+-]?\d+\.?\d*)([CF])?$', temp_str)
    if not match:
        raise ValueError(f"Invalid temperature format: {temp_str}")
    
    value = float(match.group(1))
    unit = match.group(2) or 'C'
    
    return value, unit


def fahrenheit_to_celsius(temp_f: float) -> float:
    """Convert Fahrenheit to Celsius.
    
    Args:
        temp_f: Temperature in Fahrenheit
    
    Returns:
        Temperature in Celsius
    """
    return (temp_f - 32) * 5 / 9


def celsius_to_fahrenheit(temp_c: float) -> float:
    """Convert Celsius to Fahrenheit.
    
    Args:
        temp_c: Temperature in Celsius
    
    Returns:
        Temperature in Fahrenheit
    """
    return temp_c * 9 / 5 + 32


def parse_duration(duration_str: str) -> Tuple[int, int]:
    """Parse duration string with unit.
    
    Args:
        duration_str: Duration string (e.g., "2h", "30m", "1.5h")
    
    Returns:
        Tuple of (hours, minutes)
    
    Examples:
        >>> parse_duration("2h")
        (2, 0)
        >>> parse_duration("30m")
        (0, 30)
        >>> parse_duration("1.5h")
        (1, 30)
    """
    duration_str = duration_str.strip().lower()
    
    # Match number with unit (h or m)
    match = re.match(r'^(\d+\.?\d*)([hm])$', duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}. Use format like '2h' or '30m'")
    
    value = float(match.group(1))
    unit = match.group(2)
    
    if unit == 'h':
        hours = int(value)
        minutes = int((value - hours) * 60)
        return hours, minutes
    else:  # unit == 'm'
        return 0, int(value)


class TemperatureType(click.ParamType):
    """Click parameter type for temperature with unit."""
    
    name = "temperature"
    
    def convert(self, value, param, ctx):
        """Convert temperature string to Celsius float."""
        if isinstance(value, float):
            return value
        
        try:
            temp, unit = parse_temperature(str(value))
            if unit == 'F':
                temp = fahrenheit_to_celsius(temp)
            return temp
        except ValueError as e:
            self.fail(str(e), param, ctx)


class DurationType(click.ParamType):
    """Click parameter type for duration with unit."""
    
    name = "duration"
    
    def convert(self, value, param, ctx):
        """Convert duration string to (hours, minutes) tuple."""
        if isinstance(value, tuple):
            return value
        
        try:
            return parse_duration(str(value))
        except ValueError as e:
            self.fail(str(e), param, ctx)

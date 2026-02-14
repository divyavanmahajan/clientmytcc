//! Common types used throughout the crate.

use serde::{Deserialize, Serialize};

/// Temperature units.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
pub enum TemperatureUnit {
    /// Celsius
    #[default]
    Celsius,
    /// Fahrenheit
    Fahrenheit,
}

/// Zone setpoint status.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum SetPointStatus {
    /// Following schedule
    FollowingSchedule = 0,
    /// Manual override active
    ManualOverride = 2,
}

impl From<u8> for SetPointStatus {
    fn from(value: u8) -> Self {
        match value {
            0 => Self::FollowingSchedule,
            2 => Self::ManualOverride,
            _ => Self::FollowingSchedule, // Default to schedule
        }
    }
}

/// System Quick Action mode.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum QuickAction {
    /// Economy mode
    Economy = 0,
    /// Away mode
    Away = 1,
    /// Day Off mode
    DayOff = 2,
    /// Custom mode
    Custom = 3,
    /// Heating Off mode
    HeatingOff = 4,
    /// Auto (Normal) mode - Not in spec but useful fallback
    Auto = 255,
}

impl From<u8> for QuickAction {
    fn from(value: u8) -> Self {
        match value {
            0 => Self::Economy,
            1 => Self::Away,
            2 => Self::DayOff,
            3 => Self::Custom,
            4 => Self::HeatingOff,
            _ => Self::Auto,
        }
    }
}

impl std::fmt::Display for QuickAction {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Economy => write!(f, "Economy"),
            Self::Away => write!(f, "Away"),
            Self::DayOff => write!(f, "Day Off"),
            Self::Custom => write!(f, "Custom"),
            Self::HeatingOff => write!(f, "Heating Off"),
            Self::Auto => write!(f, "Auto"),
        }
    }
}

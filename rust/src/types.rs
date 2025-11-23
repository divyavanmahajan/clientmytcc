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

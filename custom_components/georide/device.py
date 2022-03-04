"""Home Assistant representation of an GeoRide Tracker device."""
import georideapilib.objects as GeoRideTracker, GeoRideTrackerBeacon
from .const import DOMAIN as GEORIDE_DOMAIN


class Device:
    """Home Assistant representation of a GeoRide Tracker device."""

    def __init__(self, tracker):
        """Initialize GeoRideTracker device."""
        self._tracker: GeoRideTracker = tracker

    @property
    def tracker(self):
        """return the tracker"""
        return self._tracker

    @property
    def name(self) -> str:
        """Get the name."""
        return self._tracker.tracker_name

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "GeoRide"

    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = None
        if self._tracker.version == 1:
            name = "GeoRide 1"
        elif self._tracker.version == 2:
            name = "GeoRide 2"
        elif self._tracker.version == 3:
            name = "GeoRide 3"
        else:
            name = "Prototype / Unknown"
        return name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide",
            "model": self.model_name,
            "suggested_area": "Garage"
        }


    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(GEORIDE_DOMAIN, self._tracker.tracker_id)}

    def __str__(self) -> str:
        """Get string representation."""
        return f"GeoRide Device: {self.name}::{self.model_name}::{self.unique_id}"

class DeviceBeacon:
    """Home Assistant representation of a GeoRide Tracker device."""

    def __init__(self, beacon):
        """Initialize GeoRideTracker device."""
        self._beacon: GeoRideTrackerBeacon = beacon

    @property
    def beacon(self):
        """return the tracker beacon"""
        return self._beacon

    @property
    def name(self) -> str:
        """Get the name."""
        return self._beacon.name

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "GeoRide"

    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = "GeoRide Beacon"
        return name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._beacon.beacon_id)},
            "manufacturer": "GeoRide",
            "model": self.model_name,
            "suggested_area": "Garage"
        }


    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(GEORIDE_DOMAIN, "beacon", self._beacon.beacon_id)}

    def __str__(self) -> str:
        """Get string representation."""
        return f"GeoRide Device: {self.name}::{self.model_name}::{self.unique_id}"